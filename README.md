# Wrocław Tram Derailments — 15 Years of Track Failures

**Which line will get you there most safely — and what does spatial clustering reveal about the infrastructure Wrocław keeps failing to fix?**

Data pipeline collecting 20 tram derailment incidents (2011–2026) from local press archives, geocoding them via Nominatim, and overlaying them on a live GTFS tram network — to find which streets are chronic failure points and which environmental conditions trigger the most incidents.

---

## Highlights

| | |
|---|---|
| **Incidents** | 20 (2011–2026, 15-year archive) |
| **Critical hotspot** | Legnicka — 4 incidents (2× simultaneous in 2026 heat wave) |
| **Recurring bottleneck** | Pułaskiego (Krzyki) — 2 incidents, degraded track geometry |
| **Peak months** | January (7 incidents — frost) · August (4 — rail buckling) |
| **Tram lines mapped** | all Wrocław lines from live GTFS feed |
| **Geocoding** | Nominatim / OpenStreetMap — standard library only |

---

## Pipeline

```
Local press archives (wroclaw.pl, gazetawroclawska.pl)
         │
         ▼
  notebooks/01_scraper.ipynb
  · manual + semi-automated collection
  · date, time, location, lines affected, cause notes
         │
         ▼
  derailments_raw.csv
  (20 incidents, 9 fields)
         │
         ▼
  geocode.py
  · Nominatim API (OpenStreetMap)
  · intersection → lat/lon
  · fallback: street-only query
         │
         ▼
  derailments_geocoded.csv          extract_gtfs.py
  (20 incidents + lat/lon)    ←──  GTFS zip → tram_routes.geojson
                                              tram_stops.geojson
         │                                         │
         └──────────────────┬──────────────────────┘
                            ▼
                  mapa-tramwajow.html
                  (Leaflet.js dashboard)
```

---

## File structure

```
tram-derailments/
├── notebooks/
│   └── 01_scraper.ipynb     # data collection: press scraping + manual entry
├── geocode.py               # Nominatim geocoding pipeline
├── extract_gtfs.py          # GTFS → tram_routes.geojson + tram_stops.geojson
├── derailments_raw.csv      # 20 incidents: date, location, lines, cause
├── derailments_geocoded.csv # + lat/lon from Nominatim
├── tram_routes.geojson      # Wrocław tram network (generated from GTFS)
├── tram_stops.geojson       # Wrocław tram stops (generated from GTFS)
├── README.md
└── .gitignore
```

---

## Stack

- Python 3.10+
- Standard library only: `csv`, `json`, `zipfile`, `urllib`, `ssl`, `time`
- [Nominatim](https://nominatim.openstreetmap.org/) — geocoding (OpenStreetMap)
- [GTFS — Otwarte Dane Wrocław](https://www.wroclaw.pl/open-data) — tram network
- [Leaflet.js](https://leafletjs.com/) — interactive map (frontend, not in this repo)

---

## How to run

```bash
# No pip install needed — standard library only

# 1. Geocode raw incidents
python geocode.py
# reads:  derailments_raw.csv
# writes: derailments_geocoded.csv

# 2. Extract tram network from GTFS
# Download GTFS zip from https://www.wroclaw.pl/open-data/dataset/rozkladjazdytransportupublicznego
# Place it at: ../rozklady/<filename>.zip
# Update GTFS_ZIP path in extract_gtfs.py, then:
python extract_gtfs.py
# writes: tram_routes.geojson, tram_stops.geojson
```

---

## Data sources

| Source | Dataset | Licence |
|--------|---------|---------|
| [wroclaw.pl](https://wroclaw.pl) | Press releases — tram incidents | Public |
| [Gazeta Wrocławska](https://gazetawroclawska.pl) | Local press archive | Public |
| [Otwarte Dane Wrocław](https://www.wroclaw.pl/open-data) | GTFS tram schedule | Open Data (CC BY) |
| [OpenStreetMap / Nominatim](https://nominatim.openstreetmap.org) | Geocoding | ODbL |

---

*Wiktoria Gocałek · 2026 · [portfolio](https://wiktoriagocalek.github.io)*
