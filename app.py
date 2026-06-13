import streamlit as st
from ui.calentar_view import render_calendar_page
from ui.contribute_form import render_contribute_page

st.set_page_config(page_title="EDEN Commons", layout="wide")

page = st.sidebar.radio("Navegación", ["Calendar", "Contribute", "Browse"])

if page == "Calendar":
    render_calendar_page()

elif page == "Contribute":
    render_contribute_page()

elif page == "Browse":
    st.title("Browse")
    st.write("Aquí irá el explorador de recursos y publicaciones disponibles.")
