import json
import os
from connection import get_connection

SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")


def load_json(filename: str) -> list:
    with open(os.path.join(SEED_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def seed_crops(cursor, crops: list) -> int:
    cursor.executemany(
        """
        INSERT OR REPLACE INTO crops (
            id, common_name, scientific_name,
            germination_days_min, germination_days_max,
            days_to_harvest_min, days_to_harvest_max,
            optimal_soil_temp_c, water_requirement, sun_requirement,
            frost_tolerant, ph_min, ph_max, yield_kg_per_m2,
            companion_plants, incompatible_plants, notes
        ) VALUES (
            :id, :common_name, :scientific_name,
            :germination_days_min, :germination_days_max,
            :days_to_harvest_min, :days_to_harvest_max,
            :optimal_soil_temp_c, :water_requirement, :sun_requirement,
            :frost_tolerant, :ph_min, :ph_max, :yield_kg_per_m2,
            :companion_plants, :incompatible_plants, :notes
        )
        """,
        crops,
    )
    return len(crops)


def seed_entries(cursor, entries: list) -> int:
    cursor.executemany(
        """
        INSERT OR REPLACE INTO community_entries (
            id, crop_id, region, region_lat, region_lon,
            activity, lunar_condition, soil_condition,
            timing_local, timing_hemisphere, source_type,
            raw_text, structured_json, status
        ) VALUES (
            :id, :crop_id, :region, :region_lat, :region_lon,
            :activity, :lunar_condition, :soil_condition,
            :timing_local, :timing_hemisphere, :source_type,
            :raw_text, :structured_json, :status
        )
        """,
        entries,
    )
    return len(entries)


def run_seed():
    crops = load_json("crops.json")
    entries = load_json("entries.json")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        n_crops = seed_crops(cursor, crops)
        n_entries = seed_entries(cursor, entries)
        conn.commit()
    finally:
        conn.close()

    print(f"Crops insertados:            {n_crops}")
    print(f"Community entries insertados: {n_entries}")


if __name__ == "__main__":
    run_seed()
