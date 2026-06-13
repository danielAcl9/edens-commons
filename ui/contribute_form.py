import json
import streamlit as st
from db.connection import get_connection
from core.synthesis import validate_contribution


def render_contribute_page(t: dict):
    st.title(t["contribute_title"])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, common_name FROM crops")
    crops = cursor.fetchall()
    conn.close()

    crop_names = [c[1] for c in crops]

    form_key = st.session_state.get("contribute_form_key", 0)
    with st.form(f"contribute_form_{form_key}"):
        region = st.text_input(t["region"])
        selected_name = st.selectbox(t["select_crop"], crop_names)
        practice_text = st.text_area(t["practice"])
        timing = st.text_input(t["timing"])
        source = st.text_input(t["source"])
        submitted = st.form_submit_button(t["submit"])

    if submitted:
        crop_id = [c[0] for c in crops if c[1] == selected_name][0]

        form_data = {
            "region": region,
            "crop_id": crop_id,
            "practice_text": practice_text,
            "timing": timing,
            "source": source,
        }

        conn = get_connection()
        conn.row_factory = lambda cur, row: dict(zip([c[0] for c in cur.description], row))
        try:
            cur = conn.execute(
                "SELECT * FROM community_entries WHERE crop_id = ? ORDER BY created_at DESC",
                (crop_id,),
            )
            existing_entries = cur.fetchall()
        finally:
            conn.close()

        result = validate_contribution(form_data, existing_entries)
        status = result.get("status", "unverified")
        message = result.get("message", "")
        structured = result.get("structured_json") or {}

        STATUS_LABELS = {
            "verified": "✅ " + t["status_verified"],
            "unverified": "🆕 " + t["status_unverified"],
            "regional_variant": "🔄 " + t["status_regional"],
            "rejected": "❌ " + t["status_rejected"],
        }
        label = STATUS_LABELS.get(status, f"ℹ️ {status.capitalize()}")
        st.markdown(f"**{label}** — {message}")

        if status != "rejected":
            conn = get_connection()
            try:
                cur = conn.execute("SELECT COUNT(*) FROM community_entries")
                count = cur.fetchone()[0]
                new_id = f"entry_{count + 1:04d}"

                conn.execute(
                    """INSERT INTO community_entries
                       (id, crop_id, region, activity, lunar_condition, soil_condition,
                        timing_local, timing_hemisphere, source_type, raw_text, structured_json, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        new_id,
                        crop_id,
                        region,
                        structured.get("activity"),
                        structured.get("lunar_condition"),
                        structured.get("soil_condition"),
                        structured.get("timing_local"),
                        structured.get("timing_hemisphere"),
                        source or None,
                        practice_text,
                        json.dumps(structured, ensure_ascii=False) if structured else None,
                        status,
                    ),
                )
                conn.commit()

                cur = conn.execute(
                    "SELECT COUNT(*) FROM community_entries WHERE crop_id = ? AND region = ?",
                    (crop_id, region),
                )
                region_count = cur.fetchone()[0]
            finally:
                conn.close()

            st.session_state["contribute_form_key"] = form_key + 1
            st.success(
                t["thanks_message"].format(
                    crop=selected_name, region=region, count=region_count
                )
            )
            st.rerun()
