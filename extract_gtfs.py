#!/usr/bin/env python3
"""
Extract Wrocław tram routes from GTFS and save as GeoJSON for Leaflet.
Outputs: tram_routes.geojson, tram_stops.geojson
"""

import zipfile, csv, json, io
from collections import defaultdict

GTFS_ZIP = "../rozklady/OtwartyWroclaw_rozklad_jazdy_GTFS_20062026.zip"

def read_gtfs(zf, filename):
    with zf.open(filename) as f:
        text = f.read().decode("utf-8-sig")   # strips BOM
    return list(csv.DictReader(io.StringIO(text)))

print("Reading GTFS…")
with zipfile.ZipFile(GTFS_ZIP) as zf:
    routes   = read_gtfs(zf, "routes.txt")
    trips    = read_gtfs(zf, "trips.txt")
    shapes   = read_gtfs(zf, "shapes.txt")
    stops    = read_gtfs(zf, "stops.txt")

# ── 1. Tram route IDs (route_type = 0) ───────────────────────────────────────
tram_routes = {r["route_id"]: r["route_short_name"]
               for r in routes if r["route_type"].strip() == "0"}
print(f"Tram routes: {sorted(tram_routes.values(), key=lambda x: x.zfill(3))}")

# ── 2. route_id → set of shape_ids (from trips) ──────────────────────────────
route_shapes = defaultdict(set)
for t in trips:
    if t["route_id"] in tram_routes and t["shape_id"]:
        route_shapes[t["route_id"]].add(t["shape_id"])

# ── 3. shape_id → ordered list of (lat, lon) ─────────────────────────────────
print("Building shape geometries…")
shape_points = defaultdict(list)
for s in shapes:
    shape_points[s["shape_id"]].append((
        int(s["shape_pt_sequence"]),
        float(s["shape_pt_lat"]),
        float(s["shape_pt_lon"]),
    ))

# Sort by sequence
for sid in shape_points:
    shape_points[sid].sort(key=lambda x: x[0])

# ── 4. For each route pick the most representative shapes ────────────────────
#    (use longest shape per direction to avoid tiny variants)
def pick_shapes(shape_ids, n=4):
    """Return up to n largest shapes by point count."""
    ranked = sorted(shape_ids, key=lambda s: -len(shape_points[s]))
    return ranked[:n]

# ── 5. Build GeoJSON ─────────────────────────────────────────────────────────
features = []
for route_id, short_name in tram_routes.items():
    shape_ids = pick_shapes(route_shapes[route_id])
    for sid in shape_ids:
        coords = [[pt[2], pt[1]] for pt in shape_points[sid]]  # GeoJSON: [lon, lat]
        if len(coords) < 2:
            continue
        features.append({
            "type": "Feature",
            "properties": {
                "route_id":    route_id,
                "line":        short_name,
                "shape_id":    sid,
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            }
        })

geojson = {"type": "FeatureCollection", "features": features}
with open("tram_routes.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False)
print(f"tram_routes.geojson — {len(features)} line segments")

# ── 6. Tram stops ─────────────────────────────────────────────────────────────
#    stop_type 1 = tram stop in Wrocław GTFS? Check location_type field.
tram_stop_ids = set()
for t in trips:
    if t["route_id"] in tram_routes:
        pass  # we'd need stop_times for this — skip, use all stops for now

stop_features = []
for s in stops:
    try:
        lat = float(s["stop_lat"])
        lon = float(s["stop_lon"])
    except (ValueError, KeyError):
        continue
    stop_features.append({
        "type": "Feature",
        "properties": {
            "stop_id":   s.get("stop_id", ""),
            "stop_name": s.get("stop_name", ""),
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat]}
    })

stops_geojson = {"type": "FeatureCollection", "features": stop_features}
with open("tram_stops.geojson", "w", encoding="utf-8") as f:
    json.dump(stops_geojson, f, ensure_ascii=False)
print(f"tram_stops.geojson — {len(stop_features)} stops")
