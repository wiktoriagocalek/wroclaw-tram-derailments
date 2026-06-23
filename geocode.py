#!/usr/bin/env python3
"""
Geocode tram derailment locations in Wrocław using Nominatim (OpenStreetMap).
Outputs derailments_geocoded.csv with lat/lon columns.
"""

import csv
import time
import urllib.request
import urllib.parse
import json
import ssl

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

INPUT  = "derailments_raw.csv"
OUTPUT = "derailments_geocoded.csv"

HEADERS = {"User-Agent": "WiktoriaTramProject/1.0 (portfolio; wiktoriagocalek@gmail.com)"}

def nominatim_query(query):
    """Single Nominatim request → (lat, lon) or (None, None)."""
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "pl",
    })
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10, context=_ctx) as r:
        data = json.loads(r.read())
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


def build_queries(row):
    """Return list of query strings to try, from most to least specific."""
    s1 = row["street_1"].strip()
    s2 = row["street_2"].strip()
    queries = []
    if s1 and s2:
        queries.append(f"{s1} & {s2}, Wrocław, Poland")
        queries.append(f"{s1} {s2}, Wrocław, Poland")
    if s1:
        queries.append(f"{s1}, Wrocław, Poland")
    return queries


def geocode_row(row):
    for q in build_queries(row):
        print(f"  → {q}")
        lat, lon = nominatim_query(q)
        time.sleep(1.1)          # Nominatim: max 1 req/s
        if lat:
            print(f"     ✓ {lat:.5f}, {lon:.5f}")
            return lat, lon, q
    print("     ✗ not found")
    return None, None, ""


# ── main ──────────────────────────────────────────────────────────────────────
with open(INPUT, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

out_fields = [k for k in rows[0].keys() if k is not None] + ["lat", "lon", "geocode_query"]

results = []
for i, row in enumerate(rows, 1):
    print(f"\n[{i}/{len(rows)}] {row['date']} — {row['location_pl']}")
    lat, lon, query = geocode_row(row)
    clean = {k: v for k, v in row.items() if k is not None}
    results.append({**clean, "lat": lat or "", "lon": lon or "", "geocode_query": query})

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=out_fields)
    w.writeheader()
    w.writerows(results)

found = sum(1 for r in results if r["lat"])
print(f"\nDone: {found}/{len(results)} geocoded → {OUTPUT}")
