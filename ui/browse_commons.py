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


def render_browse_page(t: dict):
    st.title(t["browse_title"])

    all_entries = _load_entries()

    if not all_entries:
        st.info(t["no_entries"])
        return

    all_opt = t["filter_all"]
    crops_opts = [all_opt] + sorted({e["crop"] for e in all_entries if e.get("crop")})
    regions_opts = [all_opt] + sorted({e["region"] for e in all_entries if e.get("region")})
    statuses_opts = [all_opt] + sorted({e["status"] for e in all_entries if e.get("status")})

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_crop = st.selectbox(t["select_crop"], crops_opts)
    with col2:
        sel_region = st.selectbox(t["region"], regions_opts)
    with col3:
        sel_status = st.selectbox(t["filter_status"], statuses_opts)

    filtered = [
        e for e in all_entries
        if (sel_crop == all_opt or e.get("crop") == sel_crop)
        and (sel_region == all_opt or e.get("region") == sel_region)
        and (sel_status == all_opt or e.get("status") == sel_status)
    ]

    st.markdown(t["entries_found"].format(count=len(filtered)))

    if _HAS_PANDAS:
        df = _rows_to_df(filtered)
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(filtered, use_container_width=True)

    csv_bytes = _entries_to_csv(filtered)
    st.download_button(
        label=t["download_csv"],
        data=csv_bytes,
        file_name="edens_commons_entries.csv",
        mime="text/csv",
    )
