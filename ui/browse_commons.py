import io
import streamlit as st
from db.connection import get_connection

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False


def _load_entries() -> list[dict]:
    conn = get_connection()
    conn.row_factory = lambda cur, row: dict(zip([c[0] for c in cur.description], row))
    try:
        cur = conn.execute(
            """SELECT
                   ce.id,
                   c.common_name  AS crop,
                   ce.region,
                   ce.activity,
                   ce.raw_text    AS text,
                   ce.source_type AS source,
                   ce.status
               FROM community_entries ce
               JOIN crops c ON ce.crop_id = c.id
               ORDER BY ce.created_at DESC"""
        )
        return cur.fetchall()
    finally:
        conn.close()


def _entries_to_csv(rows: list[dict]) -> bytes:
    if not rows:
        return b"crop,region,activity,text,source,status\n"
    if _HAS_PANDAS:
        df = _rows_to_df(rows)
        return df.to_csv(index=False).encode("utf-8")
    # fallback: manual CSV
    import csv
    buf = io.StringIO()
    cols = ["crop", "region", "activity", "text", "source", "status"]
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _rows_to_df(rows: list[dict]):
    import pandas as pd
    return pd.DataFrame(rows, columns=["crop", "region", "activity", "text", "source", "status"])


def render_browse_page():
    st.title("Browse the Commons")

    all_entries = _load_entries()

    if not all_entries:
        st.info("No community entries yet. Be the first to contribute!")
        return

    crops_opts = ["All"] + sorted({e["crop"] for e in all_entries if e.get("crop")})
    regions_opts = ["All"] + sorted({e["region"] for e in all_entries if e.get("region")})
    statuses_opts = ["All"] + sorted({e["status"] for e in all_entries if e.get("status")})

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_crop = st.selectbox("Crop", crops_opts)
    with col2:
        sel_region = st.selectbox("Region", regions_opts)
    with col3:
        sel_status = st.selectbox("Status", statuses_opts)

    filtered = [
        e for e in all_entries
        if (sel_crop == "All" or e.get("crop") == sel_crop)
        and (sel_region == "All" or e.get("region") == sel_region)
        and (sel_status == "All" or e.get("status") == sel_status)
    ]

    st.markdown(f"**{len(filtered)}** entries found")

    if _HAS_PANDAS:
        df = _rows_to_df(filtered)
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(filtered, use_container_width=True)

    csv_bytes = _entries_to_csv(filtered)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_bytes,
        file_name="edens_commons_entries.csv",
        mime="text/csv",
    )
