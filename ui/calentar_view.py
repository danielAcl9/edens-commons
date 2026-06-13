import streamlit as st
from db.connection import get_connection
from core.almanac import generate_calendar_data
from core.synthesis import synthesize_calendar
from core.lunar_heuristics import LUNAR_SUGGESTIONS

def render_calendar_page():
    st.title("EDENS Commons - Almanac")

    location = st.text_input("Type in your city or location!")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, common_name FROM crops")
    crops = cursor.fetchall()
    conn.close()

    crop_names = [c[1] for c in crops]
    selected_name = st.selectbox("Select your crop", crop_names)
    crop_id = [c[0] for c in crops if c[1] == selected_name][0]

    if st.button("Generate Calendar"):
        calendar_data = generate_calendar_data(location, crop_id)
        synthesis = synthesize_calendar(calendar_data)

        st.session_state["calendar_data"] = calendar_data
        st.session_state["synthesis"] = synthesis

        st.write(f"Location found: {calendar_data['location']['name']}")
        st.write("Calendar generated succesfully!")

    if "calendar_data" in st.session_state and "synthesis" in st.session_state:
        synthesis = st.session_state["synthesis"]
        months_data = (synthesis or {}).get("months", [])

        COLORS = {
            "planting": "#8fb339",
            "fertilizing": "#d4a843",
            "harvest": "#e07b39",
            "pruning": "#9b59b6",
            "irrigation": "#4a90d9",
            "rest": "#cccccc",
            "unknown": "#eeeeee",
        }
        ICONS = {
            "planting": "🌱",
            "fertilizing": "🌿",
            "harvest": "🌾",
            "pruning": "✂️",
            "irrigation": "💧",
            "rest": "⚪",
            "unknown": "❓",
        }

        st.markdown("### Calendar Overview")
        for row_start in range(0, 12, 4):
            row_months = months_data[row_start : row_start + 4]
            cols = st.columns(4)
            for col_idx, month_info in enumerate(row_months):
                global_idx = row_start + col_idx
                month_name = month_info.get("month", f"Month {global_idx + 1}")
                activity = month_info.get("activity", "unknown")
                explanation = month_info.get("explanation", "")
                color = COLORS.get(activity, COLORS["unknown"])
                icon = ICONS.get(activity, ICONS["unknown"])

                with cols[col_idx]:
                    with st.container():
                        st.markdown(
                            f"""<div style="
                                background-color: {color};
                                border-radius: 10px;
                                padding: 12px 8px 8px 8px;
                                margin-bottom: 4px;
                                text-align: center;
                                min-height: 90px;
                            ">
                                <div style="font-size: 1.6em;">{icon}</div>
                                <div style="font-weight: bold; font-size: 0.9em; color: #222;">{month_name}</div>
                                <div style="font-size: 0.75em; color: #333; margin-top: 4px;">{activity}</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        if st.button(month_name, key=f"month_btn_{global_idx}"):
                            st.session_state["selected_month"] = global_idx

        if "selected_month" in st.session_state:
            idx = st.session_state["selected_month"]
            if idx < len(months_data):
                m = months_data[idx]
                month_name = m.get("month", "")
                activity = m.get("activity", "unknown")

                st.markdown(f"### {month_name} — {activity.capitalize()}")
                st.write(m.get("explanation", ""))

                # Lunar phases for this month
                st.markdown("#### 🌙 Lunar Phases")
                calendar_data = st.session_state["calendar_data"]
                lunar_phases = calendar_data.get("lunar_phases", [])
                month_phases = [
                    p for p in lunar_phases
                    if len(p.get("date", "")) >= 7 and int(p["date"][5:7]) == idx + 1
                ]
                if month_phases:
                    for phase in month_phases:
                        phase_key = phase.get("phase", "")
                        phase_label = "🌑 New Moon" if phase_key == "new_moon" else "🌕 Full Moon"
                        suggestion = LUNAR_SUGGESTIONS.get(phase_key, "")
                        st.markdown(
                            f"- **{phase_label}** on {phase['date']}  \n"
                            f"  _{suggestion}_"
                        )
                else:
                    st.write("No lunar events this month.")

                # Community entries for this activity
                st.markdown("#### 👥 Community Entries")
                entries = calendar_data.get("community_entries", [])
                relevant = [e for e in entries if e.get("activity") == activity]
                if relevant:
                    for entry in relevant:
                        region = entry.get("region") or "Unknown region"
                        raw_text = entry.get("raw_text") or ""
                        source_type = entry.get("source_type") or entry.get("status") or "community"
                        st.markdown(
                            f"- **{region}** _{source_type}_  \n"
                            f"  {raw_text}"
                        )
                else:
                    st.write(f"No community entries for this activity yet.")