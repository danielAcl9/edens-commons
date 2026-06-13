import streamlit as st
from db.connection import get_connection
from core.almanac import generate_calendar_data
from core.synthesis import synthesize_calendar

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
                st.markdown(f"**{m.get('month')}** — {m.get('activity', '').capitalize()}")
                st.write(m.get("explanation", ""))