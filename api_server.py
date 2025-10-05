import os
import glob
import datetime as dt
from typing import List, Dict, Optional, Tuple, Any

import numpy as np
import xarray as xr
from fastapi import FastAPI, Request, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Circle

# Import weather service
from weather_service import get_weather_data, get_pollutant_movement_prediction

# Import GROQ service for AI interpretations
from groq_service import generate_weather_interpretation, generate_prediction_interpretation


# -----------------------------
# App setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUT_DIR = os.path.join(STATIC_DIR, "outputs")

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="TEMPO Pollution Viewer", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# -----------------------------
# Domain configuration
# -----------------------------
VARIABLE_NAMES: Dict[str, str] = {
    'NO2': "product/vertical_column_troposphere",
    'CH2O': "product/vertical_column_troposphere",
    'AI': "product/aerosol_index_354_388",
    'PM': "product/aerosol_optical_depth_550",
    'O3': "product/ozone_total_column",
}

UNITS: Dict[str, str] = {
    'NO2': "molecules/cm²",
    'CH2O': "molecules/cm²",
    'AI': "index",
    'PM': "dimensionless",
    'O3': "Dobson Units",
}

POLLUTION_THRESHOLDS: Dict[str, Dict[str, float]] = {
    'NO2': {
        'moderate': 5.0e15,
        'unhealthy': 1.0e16,
        'very_unhealthy': 2.0e16,
        'hazardous': 3.0e16,
    },
    'CH2O': {
        'moderate': 8.0e15,
        'unhealthy': 1.6e16,
        'very_unhealthy': 3.2e16,
        'hazardous': 6.4e16,
    },
    'AI': {
        'moderate': 1.0,
        'unhealthy': 2.0,
        'very_unhealthy': 4.0,
        'hazardous': 7.0,
    },
    'PM': {
        'moderate': 0.2,
        'unhealthy': 0.5,
        'very_unhealthy': 1.0,
        'hazardous': 2.0,
    },
    'O3': {
        'moderate': 220,
        'unhealthy': 280,
        'very_unhealthy': 400,
        'hazardous': 500,
    },
}


# -----------------------------
# Helpers
# -----------------------------
def geocode_location(location_name: str) -> Optional[Tuple[float, float]]:
    try:
        geolocator = Nominatim(user_agent="tempo_pollution_frontend")
        location = geolocator.geocode(location_name, timeout=10)
        if location:
            return (float(location.latitude), float(location.longitude))
        return None
    except GeocoderTimedOut:
        return None
    except Exception:
        return None


# Reverse geocoding with simple in-memory cache to reduce external lookups
_reverse_cache: Dict[Tuple[float, float], Optional[str]] = {}

def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    key = (round(float(lat), 4), round(float(lon), 4))
    if key in _reverse_cache:
        return _reverse_cache[key]
    try:
        geolocator = Nominatim(user_agent="tempo_pollution_frontend_reverse")
        location = geolocator.reverse((lat, lon), timeout=10, language='en')
        name: Optional[str] = None
        if location and getattr(location, 'raw', None) and 'display_name' in location.raw:
            name = location.raw['display_name']
        elif location and getattr(location, 'address', None):
            name = str(location.address)
        _reverse_cache[key] = name
        return name
    except GeocoderTimedOut:
        _reverse_cache[key] = None
        return None
    except Exception:
        _reverse_cache[key] = None
        return None

def find_latest_file_for_gas(gas: str) -> Optional[str]:
    """Search TempData/ and TempData/{gas}/ for the most recent file."""
    candidates: List[str] = []
    tempdata_root = os.path.join(BASE_DIR, "TempData")
    # Search common subdir pattern first
    gas_dir = os.path.join(tempdata_root, gas)
    patterns = []
    if os.path.isdir(gas_dir):
        patterns.append(os.path.join(gas_dir, "**", "*.nc"))
        patterns.append(os.path.join(gas_dir, "**", "*.nc4"))
    # Also search root TempData
    patterns.append(os.path.join(tempdata_root, "**", "*.nc"))
    patterns.append(os.path.join(tempdata_root, "**", "*.nc4"))

    for pattern in patterns:
        candidates.extend(glob.glob(pattern, recursive=True))

    if not candidates:
        return None

    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


def classify_pollution_level(value: float, gas: str) -> Tuple[str, int]:
    if np.isnan(value) or gas not in POLLUTION_THRESHOLDS:
        return 'no_data', 0
    thresholds = POLLUTION_THRESHOLDS[gas]
    if value >= thresholds['hazardous']:
        return 'hazardous', 4
    elif value >= thresholds['very_unhealthy']:
        return 'very_unhealthy', 3
    elif value >= thresholds['unhealthy']:
        return 'unhealthy', 2
    elif value >= thresholds['moderate']:
        return 'moderate', 1
    else:
        return 'good', 0


def detect_hotspots(data: np.ndarray, lats: np.ndarray, lons: np.ndarray, gas: str,
                    min_cluster_size: int = 3) -> List[Dict[str, Any]]:
    hotspots: List[Dict[str, Any]] = []
    if gas not in POLLUTION_THRESHOLDS:
        return hotspots

    if lats.ndim == 1 and lons.ndim == 1:
        lon_grid, lat_grid = np.meshgrid(lons, lats)
    else:
        lat_grid = lats
        lon_grid = lons

    thresholds = POLLUTION_THRESHOLDS[gas]
    for level_name, threshold in [
        ('hazardous', thresholds['hazardous']),
        ('very_unhealthy', thresholds['very_unhealthy']),
        ('unhealthy', thresholds['unhealthy']),
        ('moderate', thresholds['moderate']),
    ]:
        mask = data >= threshold
        labeled_array, num_features = ndimage.label(mask)
        for region_id in range(1, num_features + 1):
            region_mask = labeled_array == region_id
            region_size = int(np.sum(region_mask))
            if region_size >= min_cluster_size:
                region_values = data[region_mask]
                region_lats = lat_grid[region_mask]
                region_lons = lon_grid[region_mask]
                hotspots.append({
                    'gas': gas,
                    'level': level_name,
                    'size_pixels': region_size,
                    'max_value': float(np.nanmax(region_values)),
                    'mean_value': float(np.nanmean(region_values)),
                    'center_lat': float(np.mean(region_lats)),
                    'center_lon': float(np.mean(region_lons)),
                    'lat_range': (float(np.min(region_lats)), float(np.max(region_lats))),
                    'lon_range': (float(np.min(region_lons)), float(np.max(region_lons))),
                    'area_km2': float(region_size * 2.1 * 4.4),
                })

    hotspots.sort(key=lambda x: (
        {'hazardous': 4, 'very_unhealthy': 3, 'unhealthy': 2, 'moderate': 1}[x['level']],
        x['max_value']
    ), reverse=True)
    return hotspots


def check_regional_alerts(data: np.ndarray, lats: np.ndarray, lons: np.ndarray,
                          center_lat: float, center_lon: float, radius: float,
                          gas: str, location_name: str) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    if gas not in POLLUTION_THRESHOLDS:
        return alerts

    if lats.ndim == 1 and lons.ndim == 1:
        lon_grid, lat_grid = np.meshgrid(lons, lats)
    else:
        lat_grid = lats
        lon_grid = lons

    lat_mask = np.abs(lat_grid - center_lat) <= radius
    lon_mask = np.abs(lon_grid - center_lon) <= radius
    region_mask = lat_mask & lon_mask

    if np.sum(region_mask) > 0:
        region_values = data[region_mask]
        region_values = region_values[~np.isnan(region_values)]
        if len(region_values) > 0:
            max_value = float(np.max(region_values))
            mean_value = float(np.mean(region_values))
            level, severity = classify_pollution_level(max_value, gas)
            if severity > 0:
                alerts.append({
                    'region': location_name,
                    'gas': gas,
                    'lat': center_lat,
                    'lon': center_lon,
                    'level': level,
                    'severity': severity,
                    'max_value': max_value,
                    'mean_value': mean_value,
                    'num_pixels': int(len(region_values)),
                })
    return alerts


def visualize_multi_gas(gas_data: Dict[str, Any], location_name: str,
                        center_lat: float, center_lon: float, radius: float) -> str:
    available_gases = [g for g, info in gas_data.items() if info.get('datatree') is not None]
    if not available_gases:
        return ""

    num_gases = len(available_gases)
    if num_gases == 1:
        fig, axes = plt.subplots(1, 1, figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        axes = [axes]
    elif num_gases <= 2:
        fig, axes = plt.subplots(1, 2, figsize=(20, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    elif num_gases <= 4:
        fig, axes = plt.subplots(2, 2, figsize=(20, 16), subplot_kw={'projection': ccrs.PlateCarree()})
        axes = axes.flatten()
    else:
        fig, axes = plt.subplots(2, 3, figsize=(24, 16), subplot_kw={'projection': ccrs.PlateCarree()})
        axes = axes.flatten()

    data_proj = ccrs.PlateCarree()
    extent = [center_lon - radius - 0.5, center_lon + radius + 0.5,
              center_lat - radius - 0.5, center_lat + radius + 0.5]

    for idx, gas in enumerate(available_gases):
        if idx >= len(axes):
            break
        ax = axes[idx]
        info = gas_data[gas]
        datatree = info['datatree']
        variable_name = VARIABLE_NAMES[gas]
        try:
            da = datatree[variable_name]
            lons_raw = datatree["geolocation/longitude"].values
            lats_raw = datatree["geolocation/latitude"].values
            if 'product/main_data_quality_flag' in datatree:
                quality_flag = datatree["product/main_data_quality_flag"].values
                good_data = da.where(quality_flag == 0).squeeze()
            else:
                good_data = da.squeeze()

            if lons_raw.ndim == 1 and lats_raw.ndim == 1:
                lons, lats = np.meshgrid(lons_raw, lats_raw)
            else:
                lons = lons_raw
                lats = lats_raw

            ax.set_extent(extent, crs=data_proj)
            ax.add_feature(cfeature.OCEAN, color="white", zorder=0)
            ax.add_feature(cfeature.LAND, color="white", zorder=0)
            ax.add_feature(cfeature.STATES, color="black", linewidth=1, zorder=1)
            ax.coastlines(resolution="10m", color="black", linewidth=1, zorder=1)

            vmax_val = float(np.nanpercentile(good_data, 98))
            contour = ax.contourf(
                lons, lats, good_data,
                levels=20,
                vmin=0,
                vmax=vmax_val if np.isfinite(vmax_val) and vmax_val > 0 else float(np.nanmax(good_data)),
                alpha=0.85,
                cmap='YlOrRd',
                zorder=2
            )
            # Thin black contour lines to improve readability
            try:
                ax.contour(lons, lats, good_data, levels=10, colors='k', linewidths=0.3, alpha=0.6, zorder=3)
            except Exception:
                pass
            cb = plt.colorbar(contour, ax=ax, fraction=0.046, pad=0.04)
            cb.set_label(f"{gas} ({UNITS[gas]})", fontsize=9)

            for hotspot in info.get('hotspots', [])[:5]:
                ax.plot(hotspot['center_lon'], hotspot['center_lat'], 'o',
                        color='black', markersize=6, markeredgecolor='white',
                        markeredgewidth=1, transform=data_proj, zorder=4)

            ax.plot(center_lon, center_lat, marker='*', color='black', markersize=14,
                    transform=data_proj, zorder=5)
            ax.text(center_lon, center_lat + 0.1, location_name, fontsize=9, ha='center',
                    color='black', transform=data_proj, zorder=5,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

            circle = Circle((center_lon, center_lat), radius,
                            edgecolor='black', facecolor='none', linewidth=2,
                            linestyle='--', alpha=0.8, transform=data_proj, zorder=3)
            ax.add_patch(circle)

            ax.set_title(f"{gas} Concentration", fontsize=12, weight='bold', pad=10)
        except Exception:
            ax.text(0.5, 0.5, f"Error loading {gas}", transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='red', weight='bold')

    for idx in range(len(available_gases), len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle(
        f"TEMPO Multi-Gas Analysis - {location_name}\n{dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        fontsize=14, weight='bold', y=0.98
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_name = f"analysis_{ts}.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return f"/static/outputs/{out_name}"


def visualize_tripanel_for_gas(gas: str, datatree: Any, hotspots: List[Dict[str, Any]],
                               regional_alerts: List[Dict[str, Any]],
                               thresholds: Dict[str, float]) -> str:
    data_proj = ccrs.PlateCarree()
    var_name = VARIABLE_NAMES[gas]
    da = datatree[var_name]

    lons_raw = datatree["geolocation/longitude"].values
    lats_raw = datatree["geolocation/latitude"].values
    if lons_raw.ndim == 1 and lats_raw.ndim == 1:
        lons, lats = np.meshgrid(lons_raw, lats_raw)
    else:
        lons = lons_raw
        lats = lats_raw

    qf = None
    if 'product/main_data_quality_flag' in datatree:
        qf = datatree["product/main_data_quality_flag"].values
    good_data = da.where(qf == 0).squeeze() if qf is not None else da.squeeze()

    fig = plt.figure(figsize=(24, 8))

    # Panel 1: concentration
    ax1 = fig.add_subplot(131, projection=data_proj)
    ax1.add_feature(cfeature.OCEAN, color="white", zorder=0)
    ax1.add_feature(cfeature.LAND, color="white", zorder=0)
    ax1.add_feature(cfeature.STATES, color="black", linewidth=1, zorder=1)
    ax1.coastlines(resolution="10m", color="black", linewidth=1, zorder=1)
    vmax1 = float(np.nanpercentile(good_data, 98))
    contour1 = ax1.contourf(
        lons, lats, good_data,
        levels=30,
        vmin=0,
        vmax=vmax1 if np.isfinite(vmax1) and vmax1 > 0 else float(np.nanmax(good_data)),
        alpha=0.9,
        cmap='YlOrRd',
        zorder=2
    )
    try:
        ax1.contour(lons, lats, good_data, levels=12, colors='k', linewidths=0.3, alpha=0.6, zorder=3)
    except Exception:
        pass
    cb1 = plt.colorbar(contour1, ax=ax1, fraction=0.046, pad=0.04)
    cb1.set_label(f"{gas} ({UNITS[gas]})", fontsize=10)
    ax1.set_title(f"{gas} Concentration", fontsize=12, weight='bold', pad=10)

    # Panel 2: hotspots overlay (rects approximated by center points for simplicity)
    ax2 = fig.add_subplot(132, projection=data_proj)
    ax2.add_feature(cfeature.OCEAN, color="white", zorder=0)
    ax2.add_feature(cfeature.LAND, color="white", zorder=0)
    ax2.add_feature(cfeature.STATES, color="black", linewidth=1, zorder=1)
    ax2.coastlines(resolution="10m", color="black", linewidth=1, zorder=1)
    vmax2 = float(np.nanpercentile(good_data, 98))
    contour2 = ax2.contourf(
        lons, lats, good_data,
        levels=30,
        vmin=0,
        vmax=vmax2 if np.isfinite(vmax2) and vmax2 > 0 else float(np.nanmax(good_data)),
        alpha=0.85,
        cmap='YlOrRd',
        zorder=2
    )
    try:
        ax2.contour(lons, lats, good_data, levels=10, colors='k', linewidths=0.3, alpha=0.6, zorder=3)
    except Exception:
        pass
    plt.colorbar(contour2, ax=ax2, fraction=0.046, pad=0.04)
    for i, h in enumerate([h for h in hotspots if h['gas'] == gas][:15]):
        ax2.plot(h['center_lon'], h['center_lat'], 'o', color='black',
                 markersize=6, markeredgecolor='white', markeredgewidth=1,
                 transform=data_proj, zorder=4)
        if i < 5:
            ax2.text(h['center_lon'], h['center_lat'], str(i+1), fontsize=9,
                     ha='center', va='center', color='white', weight='bold',
                     transform=data_proj, zorder=5,
                     bbox=dict(boxstyle='circle', facecolor='black', edgecolor='white', linewidth=1))
    ax2.set_title("Detected Hotspots", fontsize=12, weight='bold', pad=10)

    # Panel 3: categorical alert map
    ax3 = fig.add_subplot(133, projection=data_proj)
    ax3.add_feature(cfeature.OCEAN, color="white", zorder=0)
    ax3.add_feature(cfeature.LAND, color="white", zorder=0)
    ax3.add_feature(cfeature.STATES, color="black", linewidth=1, zorder=1)
    ax3.coastlines(resolution="10m", color="black", linewidth=1, zorder=1)
    alert_levels = np.zeros_like(good_data.values)
    for i in range(good_data.shape[0]):
        for j in range(good_data.shape[1]):
            if not np.isnan(good_data.values[i, j]):
                _, sev = classify_pollution_level(good_data.values[i, j], gas)
                alert_levels[i, j] = sev
            else:
                alert_levels[i, j] = np.nan
    contour3 = ax3.contourf(
        lons, lats, alert_levels,
        levels=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
        colors=['#2ECC71', '#F1C40F', '#E67E22', '#E74C3C', '#8E44AD'],
        alpha=0.7, zorder=2
    )
    plt.colorbar(contour3, ax=ax3, fraction=0.046, pad=0.04,
                 ticks=[0, 1, 2, 3, 4])
    ax3.set_title("Alert Levels", fontsize=12, weight='bold', pad=10)

    plt.tight_layout()
    ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_name = f"tripanel_{gas}_{ts}.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return f"/static/outputs/{out_name}"


def load_and_analyze_for_gases(gases: List[str], center_lat: float, center_lon: float,
                               radius: float, location_name: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    gas_data: Dict[str, Any] = {}
    all_hotspots: List[Dict[str, Any]] = []
    all_alerts: List[Dict[str, Any]] = []

    for gas in gases:
        data_file = find_latest_file_for_gas(gas)
        if not data_file or not os.path.exists(data_file):
            gas_data[gas] = {'datatree': None, 'data': None, 'hotspots': [], 'alerts': [], 'file': None}
            continue

        try:
            datatree = xr.open_datatree(data_file)
            var_name = VARIABLE_NAMES[gas]
            da = datatree[var_name]
            lons = datatree["geolocation/longitude"].values
            lats = datatree["geolocation/latitude"].values
            if 'product/main_data_quality_flag' in datatree:
                qf = datatree["product/main_data_quality_flag"].values
                good_data = da.where(qf == 0).squeeze()
            else:
                good_data = da.squeeze()

            hs = detect_hotspots(good_data.values, lats, lons, gas)
            alerts = check_regional_alerts(good_data.values, lats, lons, center_lat, center_lon, radius, gas, location_name)
            all_hotspots.extend(hs)
            all_alerts.extend(alerts)

            gas_data[gas] = {
                'datatree': datatree,
                'data': good_data,
                'hotspots': hs,
                'alerts': alerts,
                'file': data_file,
            }
        except Exception:
            gas_data[gas] = {'datatree': None, 'data': None, 'hotspots': [], 'alerts': [], 'file': data_file}

    return gas_data, all_hotspots, all_alerts


# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "default_gases": ['NO2', 'CH2O', 'AI', 'PM', 'O3'],
    })


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    location: Optional[str] = Form(default=""),
    latitude: Optional[str] = Form(default=""),
    longitude: Optional[str] = Form(default=""),
    radius: float = Form(default=0.3),
    gases: Optional[str] = Form(default="NO2"),
    include_weather: bool = Form(default=True),
    include_pollutant_prediction: bool = Form(default=True),
):
    location_name = location.strip() or "Custom Location"

    lat_val: Optional[float] = None
    lon_val: Optional[float] = None

    if latitude and longitude:
        try:
            lat_val = float(latitude)
            lon_val = float(longitude)
        except Exception:
            lat_val = None
            lon_val = None

    if (lat_val is None or lon_val is None) and location_name:
        coords = geocode_location(location_name)
        if coords:
            lat_val, lon_val = coords

    if lat_val is None or lon_val is None:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "default_gases": ['NO2', 'CH2O', 'AI', 'PM', 'O3'],
            "error": "Could not determine coordinates. Provide valid coordinates or a geocodable location.",
        })

    gas_list = [g.strip().upper() for g in gases.split(',') if g.strip()]
    gas_list = [g for g in gas_list if g in VARIABLE_NAMES]
    if not gas_list:
        gas_list = ['NO2']

    gas_data, all_hotspots, all_alerts = load_and_analyze_for_gases(gas_list, lat_val, lon_val, radius, location_name)
    image_url = visualize_multi_gas(gas_data, location_name, lat_val, lon_val, radius)

    # Per-gas tripanel images
    per_gas_images: List[Dict[str, str]] = []
    for gas in gas_list:
        info = gas_data.get(gas)
        if info and info.get('datatree') is not None:
            url = visualize_tripanel_for_gas(gas, info['datatree'], all_hotspots, info['alerts'], POLLUTION_THRESHOLDS.get(gas, {}))
            per_gas_images.append({"gas": gas, "url": url})

    severity = max([a['severity'] for a in all_alerts], default=0)
    severity_to_status = {0: 'Good', 1: 'Moderate', 2: 'Unhealthy for Sensitive Groups', 3: 'Very Unhealthy', 4: 'Hazardous'}
    overall_status = severity_to_status.get(severity, 'Good')

    # Enrich top hotspots with reverse geocoded place names (best-effort; skip if unavailable)
    enriched_hotspots = []
    for h in all_hotspots[:10]:
        h_with_place = dict(h)
        place = reverse_geocode(h_with_place['center_lat'], h_with_place['center_lon'])
        if place:
            h_with_place['place'] = place
        enriched_hotspots.append(h_with_place)

    # Fetch weather data if requested
    weather_data = None
    pollutant_predictions = None
    weather_interpretation = None
    prediction_interpretation = None
    
    if include_weather or include_pollutant_prediction:
        try:
            weather_data = get_weather_data(lat_val, lon_val, days=1)
            if "error" in weather_data:
                weather_data = None  # Don't show weather data if there's an error
            elif weather_data:
                # Generate AI interpretation for weather data
                try:
                    weather_interpretation = generate_weather_interpretation(weather_data, location_name)
                    if weather_interpretation:
                        print(f"Weather interpretation generated: {len(weather_interpretation)} characters")
                    else:
                        print("Weather interpretation is None")
                except Exception as e:
                    print(f"Error generating weather interpretation: {e}")
                    weather_interpretation = None
        except Exception:
            weather_data = None
    
    if include_pollutant_prediction and weather_data and "error" not in weather_data:
        try:
            pollutant_predictions = get_pollutant_movement_prediction(lat_val, lon_val)
            if "error" in pollutant_predictions:
                pollutant_predictions = None
            else:
                pollutant_predictions = pollutant_predictions.get("predictions_next_3h", [])
                
                # Generate AI interpretation for predictions
                if pollutant_predictions:
                    try:
                        prediction_interpretation = generate_prediction_interpretation(pollutant_predictions, location_name)
                        if prediction_interpretation:
                            print(f"Prediction interpretation generated: {len(prediction_interpretation)} characters")
                        else:
                            print("Prediction interpretation is None")
                    except Exception as e:
                        print(f"Error generating prediction interpretation: {e}")
                        prediction_interpretation = None
        except Exception:
            pollutant_predictions = None

    return templates.TemplateResponse("result.html", {
        "request": request,
        "image_url": image_url,
        "location": location_name,
        "coords": {"lat": lat_val, "lon": lon_val},
        "radius": radius,
        "gases": gas_list,
        "alerts": all_alerts,
        "hotspots": enriched_hotspots,
        "overall_status": overall_status,
        "units": UNITS,
        "per_gas_images": per_gas_images,
        "weather_data": weather_data,
        "pollutant_predictions": pollutant_predictions,
        "weather_interpretation": weather_interpretation,
        "prediction_interpretation": prediction_interpretation,
    })


@app.post("/api/analyze")
async def analyze_api(
    location: Optional[str] = Form(default=""),
    latitude: Optional[str] = Form(default=""),
    longitude: Optional[str] = Form(default=""),
    radius: float = Form(default=0.3),
    gases: Optional[str] = Form(default="NO2"),
):
    location_name = location.strip() or "Custom Location"
    lat_val: Optional[float] = None
    lon_val: Optional[float] = None
    if latitude and longitude:
        try:
            lat_val = float(latitude)
            lon_val = float(longitude)
        except Exception:
            lat_val = None
            lon_val = None
    if (lat_val is None or lon_val is None) and location_name:
        coords = geocode_location(location_name)
        if coords:
            lat_val, lon_val = coords
    if lat_val is None or lon_val is None:
        return JSONResponse({"error": "Invalid coordinates or location"}, status_code=400)

    gas_list = [g.strip().upper() for g in gases.split(',') if g.strip()]
    gas_list = [g for g in gas_list if g in VARIABLE_NAMES]
    if not gas_list:
        gas_list = ['NO2']

    gas_data, all_hotspots, all_alerts = load_and_analyze_for_gases(gas_list, lat_val, lon_val, radius, location_name)
    image_url = visualize_multi_gas(gas_data, location_name, lat_val, lon_val, radius)
    return {
        "location": location_name,
        "coordinates": {"latitude": lat_val, "longitude": lon_val},
        "gases": gas_list,
        "overall_status": max([a['severity'] for a in all_alerts], default=0),
        "alerts": all_alerts,
        "hotspots": all_hotspots,
        "image_url": image_url,
    }


def hotspots_to_geojson(hotspots: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [h['center_lon'], h['center_lat']]},
                "properties": {
                    "gas": h['gas'],
                    "level": h['level'],
                    "max_value": h['max_value'],
                    "mean_value": h['mean_value'],
                    "area_km2": h['area_km2'],
                    "place": h.get('place')
                }
            }
            for h in hotspots
        ]
    }


@app.get("/api/hotspots")
async def api_hotspots(
    location: Optional[str] = Query(default=""),
    latitude: Optional[float] = Query(default=None),
    longitude: Optional[float] = Query(default=None),
    radius: float = Query(default=0.3),
    gases: Optional[str] = Query(default="NO2"),
):
    location_name = location.strip() or "Custom Location"
    lat_val = latitude
    lon_val = longitude
    if (lat_val is None or lon_val is None) and location_name:
        coords = geocode_location(location_name)
        if coords:
            lat_val, lon_val = coords
    if lat_val is None or lon_val is None:
        return JSONResponse({"type": "FeatureCollection", "features": []})

    gas_list = [g.strip().upper() for g in (gases or "NO2").split(',') if g.strip()]
    gas_list = [g for g in gas_list if g in VARIABLE_NAMES]
    if not gas_list:
        gas_list = ['NO2']

    _, _, _ = load_and_analyze_for_gases(gas_list, lat_val, lon_val, radius, location_name)
    _, hotspots, _ = load_and_analyze_for_gases(gas_list, lat_val, lon_val, radius, location_name)
    # Best-effort reverse geocode a subset to limit requests
    for h in hotspots[:20]:
        h['place'] = reverse_geocode(h['center_lat'], h['center_lon'])
    return hotspots_to_geojson(hotspots)


# -----------------------------
# Weather API Endpoints
# -----------------------------
@app.get("/api/weather")
async def api_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(1, description="Number of forecast days")
):
    """
    Get current weather conditions and forecast data for a specific location.
    Integrates with WeatherAPI.com to provide real-time weather data.
    """
    return get_weather_data(lat, lon, days)


@app.get("/api/pollutant_movement")
async def api_pollutant_movement(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate")
):
    """
    Predict air quality movement and concentration changes based on wind patterns.
    Uses weather data to forecast pollutant dispersion for the next 3 hours.
    """
    return get_pollutant_movement_prediction(lat, lon)


@app.get("/api/combined_analysis")
async def api_combined_analysis(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    radius: float = Query(0.3, description="Analysis radius in degrees"),
    gases: Optional[str] = Query("NO2", description="Comma-separated list of gases to analyze")
):
    """
    Combined analysis providing both satellite pollution data and weather information.
    This endpoint integrates TEMPO satellite data with real-time weather conditions.
    """
    # Get weather data
    weather_data = get_weather_data(lat, lon, days=1)
    
    # Get satellite pollution data
    gas_list = [g.strip().upper() for g in (gases or "NO2").split(',') if g.strip()]
    gas_list = [g for g in gas_list if g in VARIABLE_NAMES]
    if not gas_list:
        gas_list = ['NO2']
    
    location_name = "Combined Analysis Location"
    gas_data, all_hotspots, all_alerts = load_and_analyze_for_gases(gas_list, lat, lon, radius, location_name)
    
    # Create combined response
    result = {
        "location": {
            "latitude": lat,
            "longitude": lon,
            "name": location_name
        },
        "weather": weather_data,
        "satellite_data": {
            "gases_analyzed": gas_list,
            "alerts": all_alerts,
            "hotspots": all_hotspots[:10],  # Top 10 hotspots
            "overall_status": max([a['severity'] for a in all_alerts], default=0)
        },
        "analysis_timestamp": dt.datetime.utcnow().isoformat()
    }
    
    return result


# Dev server hint:
# uvicorn api_server:app --reload --host 0.0.0.0 --port 8000


