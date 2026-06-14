import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "eden_commons.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS crops (
                id                      TEXT PRIMARY KEY,
                common_name             TEXT NOT NULL,
                scientific_name         TEXT,
                germination_days_min    INTEGER,
                germination_days_max    INTEGER,
                days_to_harvest_min     INTEGER,
                days_to_harvest_max     INTEGER,
                optimal_soil_temp_c     REAL,
                water_requirement       TEXT,
                sun_requirement         TEXT,
                frost_tolerant          BOOLEAN,
                ph_min                  REAL,
                ph_max                  REAL,
                yield_kg_per_m2         REAL,
                companion_plants        TEXT,
                incompatible_plants     TEXT,
                notes                   TEXT
            );

            CREATE TABLE IF NOT EXISTS community_entries (
                id                  TEXT PRIMARY KEY,
                crop_id             TEXT REFERENCES crops(id),
                region              TEXT NOT NULL,
                region_lat          REAL,
                region_lon          REAL,
                activity            TEXT,
                lunar_condition     TEXT,
                soil_condition      TEXT,
                timing_local        TEXT,
                timing_hemisphere   TEXT,
                source_type         TEXT,
                raw_text            TEXT NOT NULL,
                structured_json     TEXT,
                status              TEXT DEFAULT 'unverified',
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS calendar_cache (
                id              TEXT PRIMARY KEY,
                crop_id         TEXT,
                lat             REAL,
                lon             REAL,
                year            INTEGER,
                calendar_json   TEXT,
                generated_at    TIMESTAMP,
                expires_at      TIMESTAMP
            );
        """)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()