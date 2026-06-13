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