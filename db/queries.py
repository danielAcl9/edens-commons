import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import json
from datetime import datetime, timedelta, timezone


from db.connection import get_connection


def _cache_id(crop_id: str, lat: float, lon: float, year: int) -> str:
    raw = f"{crop_id}|{lat}|{lon}|{year}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_cached_calendar(crop_id: str, lat: float, lon: float, year: int) -> dict | None:
    cache_id = _cache_id(crop_id, lat, lon, year)
    conn = get_connection()
    conn.row_factory = lambda cur, row: dict(zip([c[0] for c in cur.description], row))
    try:
        cur = conn.execute(
            "SELECT calendar_json, expires_at FROM calendar_cache WHERE id = ?",
            (cache_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc).replace(tzinfo=None) > expires_at:
        return None

    return json.loads(row["calendar_json"])


def save_calendar_cache(
    crop_id: str, lat: float, lon: float, year: int, calendar_data: dict
) -> None:
    cache_id = _cache_id(crop_id, lat, lon, year)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = now + timedelta(days=7)

    conn = get_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO calendar_cache
               (id, crop_id, lat, lon, year, calendar_json, generated_at, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cache_id,
                crop_id,
                lat,
                lon,
                year,
                json.dumps(calendar_data, ensure_ascii=False),
                now.isoformat(),
                expires_at.isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()
