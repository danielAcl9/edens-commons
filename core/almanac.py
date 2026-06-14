import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
import ephem
from collections import defaultdict
from datetime import date, datetime

from db.connection import get_connection
from db.queries import get_cached_calendar, save_calendar_cache


def _geocode(location_name: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "eden-commons"}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"No geocoding results for '{location_name}'")
    r = results[0]
    return {"name": r.get("display_name", location_name), "lat": float(r["lat"]), "lon": float(r["lon"])}


def _fetch_climate(lat: float, lon: float) -> list:
    today = date.today()
    start = date(today.year - 1, 1, 1)
    end = date(today.year - 1, 12, 31)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = [
        ("latitude", lat),
        ("longitude", lon),
        ("daily", "temperature_2m_max"),
        ("daily", "temperature_2m_min"),
        ("daily", "precipitation_sum"),
        ("timezone", "auto"),
        ("start_date", str(start)),
        ("end_date", str(end)),
    ]
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    daily = resp.json().get("daily", {})
    days = daily.get("time", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])

    agg = defaultdict(lambda: {"tmax": [], "tmin": [], "prec": []})
    for i, d in enumerate(days):
        ym = d[:7]
        if i < len(t_max) and t_max[i] is not None:
            agg[ym]["tmax"].append(t_max[i])
        if i < len(t_min) and t_min[i] is not None:
            agg[ym]["tmin"].append(t_min[i])
        if i < len(precip) and precip[i] is not None:
            agg[ym]["prec"].append(precip[i])

    return [
        {
            "month": ym,
            "temp_max_c": round(max(v["tmax"]), 2) if v["tmax"] else None,
            "temp_min_c": round(min(v["tmin"]), 2) if v["tmin"] else None,
            "precipitation_mm": round(sum(v["prec"]), 2) if v["prec"] else None,
        }
        for ym, v in sorted(agg.items())
    ]


def _lunar_phases_next_12() -> list:
    phases = []
    cursor = ephem.now()
    while len(phases) < 24:
        next_new = ephem.next_new_moon(cursor)
        next_full = ephem.next_full_moon(cursor)
        if next_new < next_full:
            phases.append({"phase": "new_moon", "date": next_new.datetime().strftime("%Y-%m-%d")})
            cursor = next_new + 1
        else:
            phases.append({"phase": "full_moon", "date": next_full.datetime().strftime("%Y-%m-%d")})
            cursor = next_full + 1
        if len(phases) >= 24:
            break
    return phases


def _fetch_crop(crop_id: str) -> dict:
    conn = get_connection()
    conn.row_factory = lambda cur, row: dict(zip([c[0] for c in cur.description], row))
    try:
        cur = conn.execute("SELECT * FROM crops WHERE id = ?", (crop_id,))
        row = cur.fetchone()
    finally:
        conn.close()
    if row is None:
        raise ValueError(f"Crop '{crop_id}' not found in database")
    return row


def _fetch_community_entries(crop_id: str) -> list:
    conn = get_connection()
    conn.row_factory = lambda cur, row: dict(zip([c[0] for c in cur.description], row))
    try:
        cur = conn.execute(
            "SELECT * FROM community_entries WHERE crop_id = ? ORDER BY created_at DESC",
            (crop_id,),
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return rows


def generate_calendar_data(location_name: str, crop_id: str) -> dict:
    # _geocode raises ValueError with 'No geocoding results' on bad input — let it propagate
    location = _geocode(location_name)
    lat = location["lat"]
    lon = location["lon"]
    year = date.today().year

    cached = get_cached_calendar(crop_id, lat, lon, year)
    if cached is not None:
        return cached

    try:
        climate = _fetch_climate(lat, lon)
    except Exception:
        climate = []

    try:
        lunar_phases = _lunar_phases_next_12()
    except Exception:
        lunar_phases = []

    crop_data = _fetch_crop(crop_id)
    community_entries = _fetch_community_entries(crop_id)

    result = {
        "location": location,
        "climate": climate,
        "lunar_phases": lunar_phases,
        "crop_data": crop_data,
        "community_entries": community_entries,
    }

    save_calendar_cache(crop_id, lat, lon, year, result)
    return result
