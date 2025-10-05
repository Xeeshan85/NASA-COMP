# 🌍 AERIS — Air Emissions Regional Intelligence System

**AERIS** is a FastAPI-powered web application that analyzes **NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution)** satellite data to detect, classify, and visualize air pollution levels over wildfire-affected regions.  

Originally focused on the **Madre Wildfire Region (New Cuyama, California)**, the system can be adapted to monitor any geographic area and time window.  

It integrates **NASA Harmony API**, **scientific data processing**, and **interactive web visualization** to provide real-time regional air quality intelligence.

---

## 🛰️ Key Features

### 🔹 NASA TEMPO Integration
- Automatically retrieves **NO₂ Level-3** datasets via **NASA Harmony API**
- Works with existing `.nc` NetCDF data (stored in `TempData/`)

### 🔹 Pollution & Hotspot Detection
- Applies **region-based thresholding** to identify pollution hotspots  
- Uses **connected-region labeling (SciPy)** for spatial clustering  
- Supports wildfire-specific detection thresholds for accurate classification

### 🔹 Air Quality Intelligence
- Generates detailed **air quality summaries**, **regional alerts**, and **health guidance**
- Classifies severity into: *Low, Moderate, Unhealthy, Very Unhealthy, Hazardous*

### 🔹 Visualization & Web Dashboard
- Interactive visualization using **Matplotlib** + **Cartopy**
- Clean **web interface** served via **FastAPI** + **Jinja2**
- Heatmaps, hotspot overlays, and alert panels rendered directly in browser

### 🔹 Modular & Reusable
- Clear separation of computational core (`nasa_comp.py`) and web layer (`main.py`)
- Reusable components for data loading, visualization, and reporting

---

## 🧩 System Architecture

| Layer | Components | Description |
|--------|-------------|-------------|
| **Web Server** | FastAPI + Uvicorn | Serves web dashboard and handles requests |
| **Frontend** | Jinja2 templates, CSS | Displays results (`index.html`, `result.html`, `route.html`) |
| **Computation** | NumPy, SciPy, Xarray | Handles NASA TEMPO data parsing and analysis |
| **Visualization** | Matplotlib, Cartopy | Generates pollution heatmaps and geospatial overlays |
| **Storage** | NetCDF (`.nc`) files | Stored in `TempData/` for caching and offline use |

---

## 📂 Project Structure

```
AERIS/
├── main.py               # FastAPI entry point
├── api_server.py          # Core NASA TEMPO data logic (pollution analysis)
├── templates/
│   ├── index.html        # Input interface / home page
│   ├── result.html       # Pollution result display
│   └── route.html        # Visualization / map page
├── static/
│   └── style.css         # Web styling
├── TempData/
│   ├── 117303683_TEMPO_NO2_L3_V03_20250703T190954Z_S011_subsetted.nc4  # Cached TEMPO data
│   └── 117303684_TEMPO_NO2_L3_V03_20250703T200954Z_S012_subsetted.nc4
├── requirements.txt
├── tempo_all.py
├── TEMPO.py
├── GroundSensorAnalysis.py
└── README.md
```

---

## ⚙️ Requirements

### 🧰 Dependencies
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
jinja2==3.1.4
geopy==2.4.1
numpy==1.26.4
scipy==1.13.1
xarray==2024.7.0
matplotlib==3.8.4
cartopy==0.22.0
datatree==0.1.3
requests==2.32.3
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### 1️⃣ Start the FastAPI Server
```bash
uvicorn main:app --reload
```

### 2️⃣ Access in Browser
```
http://127.0.0.1:8000
```

### 3️⃣ View Pages
| URL | Description |
|------|-------------|
| `/` | Home page (input and description) |
| `/result` | Displays detected pollution metrics and alerts |
| `/route` | Shows interactive pollution visualization |

---

## 🧠 How It Works

1. **User Request:**  
   User accesses AERIS dashboard via web interface.  

2. **Data Retrieval:**  
   - App authenticates with **NASA Earthdata** (Harmony API).  
   - Retrieves or loads existing `.nc` TEMPO NO₂ dataset from `TempData/`.  

3. **Data Processing:**  
   - Converts NetCDF data to **xarray Dataset**  
   - Normalizes NO₂ column density values  
   - Detects spatial clusters via **SciPy connected components**  

4. **Alert Generation:**  
   - Computes mean and max NO₂ per region  
   - Assigns severity classification  
   - Generates health advisory text  

5. **Visualization:**  
   - Renders geospatial map using **Cartopy**  
   - Annotates hotspots and region boundaries  
   - Displays results interactively via FastAPI templates  

---

## 📊 Example Console Output

```
🛰️ Dataset: NASA TEMPO (NO₂ Level-3)
📅 Date Range: 2025-09-15 → 2025-09-20
🌍 Region: Madre Wildfire, New Cuyama, CA

🚨 ALERT: BAKERSFIELD - HAZARDOUS
📍 35.3733°N, 119.0187°W
NO₂: 3.02e+16 molecules/cm²
⚠️ ACTION: STAY INDOORS! Dangerous air quality detected.
```

---

## 🖼️ Example Visualization

Output map (`madre_wildfire_pollution_analysis.png`) includes:
- Pollution heatmap (NO₂ intensity)
- Highlighted hotspots
- Regional boundaries and coordinate labels
- City-specific alerts overlayed

---

## 🧩 Customization

| Parameter | Location | Description |
|------------|-----------|-------------|
| `SPATIAL_BOUNDS` | `nasa_comp.py` | Defines lat/lon range for analysis |
| `TIME_CONFIG` | `nasa_comp.py` | Start & end date for TEMPO data retrieval |
| `thresholds` | Internal constants | Adjusts NO₂ severity levels |
| `TEMPLATES` | `templates/` | Modify HTML layout for web UI |

---

## 🧠 Future Enhancements
- Integration with **real-time wildfire APIs (NASA FIRMS)**  
- Multi-pollutant support (O₃, CO, SO₂)  
- Database logging (PostgreSQL + GeoJSON export)  
- REST endpoints for external data access  

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch (`feature/your-feature-name`)  
3. Add changes and tests  
4. Submit a pull request  

Follow PEP8 style guidelines and ensure your code is documented.

---

## 📄 License

MIT License  
© 2025 Xeeshan85  

Developed as part of a research initiative to enhance **environmental intelligence and wildfire response** using open NASA data.

---

## 🧭 Credits

- **NASA TEMPO** — Tropospheric Emissions: Monitoring of Pollution  
- **NASA Harmony API** — Data Access and Retrieval  
- **Cartopy & Xarray** — Geospatial and scientific computing libraries  
- **FastAPI** — High-performance web framework for the dashboard  
