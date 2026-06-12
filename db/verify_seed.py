from connection import get_connection

CROP_ID = "maize"
SEP = "-" * 60


def print_counts(cursor):
    cursor.execute("SELECT COUNT(*) FROM crops")
    n_crops = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM community_entries")
    n_entries = cursor.fetchone()[0]
    print(f"Total crops:             {n_crops}")
    print(f"Total community_entries: {n_entries}")


def print_crop(cursor, crop_id: str):
    cursor.execute("SELECT * FROM crops WHERE id = ?", (crop_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"Cultivo '{crop_id}' no encontrado.")
        return
    cols = [d[0] for d in cursor.description]
    print(f"\nCultivo: {crop_id}")
    print(SEP)
    for col, val in zip(cols, row):
        print(f"  {col:<28} {val}")


def print_entries(cursor, crop_id: str):
    cursor.execute(
        "SELECT * FROM community_entries WHERE crop_id = ? ORDER BY id",
        (crop_id,),
    )
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    print(f"\nCommunity entries para '{crop_id}' ({len(rows)} registros)")
    for row in rows:
        print(SEP)
        for col, val in zip(cols, row):
            print(f"  {col:<28} {val}")
    print(SEP)


def main():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        print_counts(cursor)
        print_crop(cursor, CROP_ID)
        print_entries(cursor, CROP_ID)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
