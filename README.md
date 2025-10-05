# AERIS - Air Emissions Regional Intelligence SystemExcellent. Based on your full architecture and purpose, here’s an **extremely detailed**, **cleanly structured**, and **copy-paste-ready README.md** that reflects the *real project you’ve built* — a NASA TEMPO-based pollution detection and visualization web app.



A web-based application for analyzing NASA TEMPO satellite data to monitor air pollution levels and detect pollution hotspots in real-time.I’ve also proposed a better project name:



## Overview> 🌍 **AERIS** — *Air Emissions Regional Intelligence System*



AERIS is a FastAPI-powered web application that processes NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution) satellite data to provide comprehensive air quality analysis. The system combines satellite data processing, weather integration, and interactive visualization to deliver actionable air quality intelligence.It’s short, professional, NASA-style, and fits your system perfectly.

You can of course rename it if you prefer (I’ll use **AERIS** throughout below).

## Features

---

### Core Capabilities

- **Multi-Gas Analysis**: Support for NO₂, CH₂O, AI (Aerosol Index), PM, and O₃ pollutants```markdown

- **Hotspot Detection**: Automated identification and classification of pollution clusters# 🌍 AERIS — Air Emissions Regional Intelligence System

- **Real-time Weather Integration**: Current weather conditions and pollutant movement prediction

- **Interactive Mapping**: Live hotspot visualization with Leaflet.js**AERIS** is a FastAPI-powered web application that analyzes **NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution)** satellite data to detect, classify, and visualize air pollution levels over wildfire-affected regions.  

- **Route Safety Analysis**: Air quality assessment for travel routes

Originally focused on the **Madre Wildfire Region (New Cuyama, California)**, the system can be adapted to monitor any geographic area and time window.  

### Data Processing

- NetCDF data parsing and analysis using xarrayIt integrates **NASA Harmony API**, **scientific data processing**, and **interactive web visualization** to provide real-time regional air quality intelligence.

- Pollution threshold classification (Good, Moderate, Unhealthy, Very Unhealthy, Hazardous)

- Spatial clustering with SciPy for hotspot detection---

- Geographic coordinate handling and reverse geocoding

## 🛰️ Key Features

### Visualization

- Multi-gas concentration heatmaps### 🔹 NASA TEMPO Integration

- Tripanel analysis figures per gas- Automatically retrieves **NO₂ Level-3** datasets via **NASA Harmony API**

- Interactive web maps with pollution overlays- Works with existing `.nc` NetCDF data (stored in `TempData/`)

- Automated report generation with AI interpretations

### 🔹 Pollution & Hotspot Detection

## Project Structure- Applies **region-based thresholding** to identify pollution hotspots  

- Uses **connected-region labeling (SciPy)** for spatial clustering  

```- Supports wildfire-specific detection thresholds for accurate classification

AERIS/

├── api_server.py              # Main FastAPI application### 🔹 Air Quality Intelligence

├── weather_service.py         # Weather data integration- Generates detailed **air quality summaries**, **regional alerts**, and **health guidance**

├── groq_service.py           # AI interpretation service  - Classifies severity into: *Low, Moderate, Unhealthy, Very Unhealthy, Hazardous*

├── pollutant_predictor.py    # Pollutant movement prediction

├── TEMPO.py                  # NASA TEMPO data processing### 🔹 Visualization & Web Dashboard

├── GroundSensorAnalysis.py   # Ground sensor integration- Interactive visualization using **Matplotlib** + **Cartopy**

├── templates/- Clean **web interface** served via **FastAPI** + **Jinja2**

│   ├── index.html           # Main input interface- Heatmaps, hotspot overlays, and alert panels rendered directly in browser

│   ├── result.html          # Analysis results display

│   └── route.html           # Route safety analysis### 🔹 Modular & Reusable

├── static/- Clear separation of computational core (`nasa_comp.py`) and web layer (`main.py`)

│   ├── style.css           # Web styling- Reusable components for data loading, visualization, and reporting

│   └── outputs/            # Generated analysis images

├── TempData/               # Cached TEMPO data files---

├── requirements.txt

└── README.md## 🧩 System Architecture

```

| Layer | Components | Description |

## Installation|--------|-------------|-------------|

| **Web Server** | FastAPI + Uvicorn | Serves web dashboard and handles requests |

1. **Clone the repository**| **Frontend** | Jinja2 templates, CSS | Displays results (`index.html`, `result.html`, `route.html`) |

```bash| **Computation** | NumPy, SciPy, Xarray | Handles NASA TEMPO data parsing and analysis |

git clone https://github.com/Xeeshan85/air-emissions-regional-intelligence-system.git| **Visualization** | Matplotlib, Cartopy | Generates pollution heatmaps and geospatial overlays |

cd AERIS| **Storage** | NetCDF (`.nc`) files | Stored in `TempData/` for caching and offline use |

```

---

2. **Install dependencies**

```bash## 📂 Project Structure

pip install -r requirements.txt

``````



3. **Set up environment variables**AERIS/

Create a `.env` file with your API keys:├── main.py               # FastAPI entry point

```├── nasa_comp.py          # Core NASA TEMPO data logic (pollution analysis)

WEATHER_API_KEY=your_weather_api_key├── templates/

GROQ_API_KEY=your_groq_api_key│   ├── index.html        # Input interface / home page

```│   ├── result.html       # Pollution result display

│   └── route.html        # Visualization / map page

## Usage├── static/

│   └── style.css         # Web styling

### Starting the Application├── TempData/

│   ├── tempo_data_1.nc   # Cached TEMPO data

```bash│   └── tempo_data_2.nc

uvicorn api_server:app --reload --host 0.0.0.0 --port 8000├── requirements.txt

```└── README.md



Access the application at `http://localhost:8000````



### Web Interface---



1. **Main Analysis** (`/`): Enter location coordinates or place names to analyze air quality## ⚙️ Requirements

2. **Route Analysis** (`/route`): Assess air quality along travel routes

3. **API Endpoints**: RESTful API for programmatic access### 🧰 Dependencies

```

### API Endpoints

fastapi==0.115.0

- `GET /api/weather` - Current weather datauvicorn[standard]==0.30.6

- `GET /api/pollutant_movement` - Pollutant dispersion predictionjinja2==3.1.4

- `GET /api/combined_analysis` - Integrated satellite and weather analysisgeopy==2.4.1

- `GET /api/hotspots` - Pollution hotspot data in GeoJSON formatnumpy==1.26.4

scipy==1.13.1

## Configurationxarray==2024.7.0

matplotlib==3.8.4

### Analysis Parameterscartopy==0.22.0

- **Radius**: Analysis area radius in degrees (default: 0.3°)datatree==0.1.3

- **Gases**: Comma-separated list of pollutants to analyzerequests==2.32.3

- **Weather Integration**: Enable/disable real-time weather data

- **Prediction**: Enable/disable pollutant movement forecasting````



### Pollution ThresholdsInstall all dependencies:

Thresholds are defined in `api_server.py` and can be customized for different pollutants:```bash

- NO₂: 5.0e15 - 3.0e16 molecules/cm²pip install -r requirements.txt

- CH₂O: 8.0e15 - 6.4e16 molecules/cm²````

- AI: 1.0 - 7.0 index

- PM: 0.2 - 2.0 dimensionless---

- O₃: 220 - 500 Dobson Units

## 🚀 Running the Application

## Data Sources

### 1️⃣ Start the FastAPI Server

- **NASA TEMPO**: Tropospheric pollution measurements

- **WeatherAPI.com**: Real-time weather conditions```bash

- **OpenStreetMap**: Base mapping datauvicorn main:app --reload

- **OSRM**: Route optimization services```



## Dependencies### 2️⃣ Access in Browser



Key packages include:```

- FastAPI and Uvicorn for web frameworkhttp://127.0.0.1:8000

- xarray and netCDF4 for satellite data processing```

- matplotlib and cartopy for visualization

- scipy and numpy for scientific computing### 3️⃣ View Pages

- geopy for geocoding services

| URL       | Description                                    |

See `requirements.txt` for complete dependency list.| --------- | ---------------------------------------------- |

| `/`       | Home page (input and description)              |

## Contributing| `/result` | Displays detected pollution metrics and alerts |

| `/route`  | Shows interactive pollution visualization      |

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/new-feature`)---

3. Commit changes (`git commit -am 'Add new feature'`)

4. Push to branch (`git push origin feature/new-feature`)## 🧠 How It Works

5. Create a Pull Request

1. **User Request:**

## License   User accesses AERIS dashboard via web interface.



This project is licensed under the MIT License - see the LICENSE file for details.2. **Data Retrieval:**



## Acknowledgments   * App authenticates with **NASA Earthdata** (Harmony API).

   * Retrieves or loads existing `.nc` TEMPO NO₂ dataset from `TempData/`.

- NASA TEMPO mission for satellite data

- NASA Earthdata for data access infrastructure3. **Data Processing:**

- WeatherAPI.com for weather services

- Open source geospatial community   * Converts NetCDF data to **xarray Dataset**
   * Normalizes NO₂ column density values
   * Detects spatial clusters via **SciPy connected components**

4. **Alert Generation:**

   * Computes mean and max NO₂ per region
   * Assigns severity classification
   * Generates health advisory text

5. **Visualization:**

   * Renders geospatial map using **Cartopy**
   * Annotates hotspots and region boundaries
   * Displays results interactively via FastAPI templates

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

* Pollution heatmap (NO₂ intensity)
* Highlighted hotspots
* Regional boundaries and coordinate labels
* City-specific alerts overlayed

---

## 🧩 Customization

| Parameter        | Location           | Description                               |
| ---------------- | ------------------ | ----------------------------------------- |
| `SPATIAL_BOUNDS` | `nasa_comp.py`     | Defines lat/lon range for analysis        |
| `TIME_CONFIG`    | `nasa_comp.py`     | Start & end date for TEMPO data retrieval |
| `thresholds`     | Internal constants | Adjusts NO₂ severity levels               |
| `TEMPLATES`      | `templates/`       | Modify HTML layout for web UI             |

---

## 🧠 Future Enhancements

* Integration with **real-time wildfire APIs (NASA FIRMS)**
* Multi-pollutant support (O₃, CO, SO₂)
* Database logging (PostgreSQL + GeoJSON export)
* REST endpoints for external data access

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

* **NASA TEMPO** — Tropospheric Emissions: Monitoring of Pollution
* **NASA Harmony API** — Data Access and Retrieval
* **Cartopy & Xarray** — Geospatial and scientific computing libraries
* **FastAPI** — High-performance web framework for the dashboard

---

> *“Turning satellite data into environmental intelligence — one map at a time.”*
> — **AERIS Team**

```

---



