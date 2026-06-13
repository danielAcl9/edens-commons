import streamlit as st
from ui.calendar_view import render_calendar_page
from ui.contribute_form import render_contribute_page
from ui.browse_commons import render_browse_page

st.set_page_config(page_title="EDEN Commons", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

TRANSLATIONS = {
    "English": {
        # Navigation
        "calendar": "Calendar",
        "contribute": "Contribute",
        "browse": "Browse",
        # Calendar page
        "calendar_title": "EDEN Commons — Almanac",
        "location_placeholder": "Type your location...",
        "select_crop": "Select your crop",
        "generate": "Generate Calendar",
        "calendar_overview": "Calendar Overview",
        "lunar_phases": "Lunar Phases",
        "new_moon": "New Moon",
        "full_moon": "Full Moon",
        "no_lunar_events": "No lunar events this month.",
        "community_entries": "Community Entries",
        "unknown_region": "Unknown region",
        "no_community_entries": "No community entries for this activity yet.",
        # Contribute page
        "contribute_title": "Contribute your knowledge",
        "region": "Your region",
        "practice": "Your practice",
        "timing": "When does this apply?",
        "source": "Source (optional)",
        "submit": "Submit",
        "status_verified": "Verified",
        "status_unverified": "New knowledge",
        "status_regional": "Regional variant",
        "status_rejected": "Rejected",
        "thanks_message": (
            "Thanks — your entry is now visible to others searching "
            "**{crop}** in **{region}**. "
            "There are now **{count}** entries for this crop in this region."
        ),
        # Browse page
        "browse_title": "Browse the Commons",
        "no_entries": "No community entries yet. Be the first to contribute!",
        "filter_all": "All",
        "filter_status": "Status",
        "entries_found": "**{count}** entries found",
        "download_csv": "⬇️ Download as CSV",
    },
    "Español": {
        # Navigation
        "calendar": "Calendario",
        "contribute": "Contribuir",
        "browse": "Explorar",
        # Calendar page
        "calendar_title": "EDEN Commons — Almanaque",
        "location_placeholder": "Escribe tu ubicación...",
        "select_crop": "Selecciona tu cultivo",
        "generate": "Generar Calendario",
        "calendar_overview": "Vista del Calendario",
        "lunar_phases": "Fases Lunares",
        "new_moon": "Luna Nueva",
        "full_moon": "Luna Llena",
        "no_lunar_events": "Sin eventos lunares este mes.",
        "community_entries": "Entradas de la Comunidad",
        "unknown_region": "Región desconocida",
        "no_community_entries": "Sin entradas comunitarias para esta actividad todavía.",
        # Contribute page
        "contribute_title": "Comparte tu conocimiento",
        "region": "Tu región",
        "practice": "Tu práctica",
        "timing": "¿Cuándo aplica?",
        "source": "Fuente (opcional)",
        "submit": "Enviar",
        "status_verified": "Verificado",
        "status_unverified": "Conocimiento nuevo",
        "status_regional": "Variante regional",
        "status_rejected": "Rechazado",
        "thanks_message": (
            "Gracias — tu entrada ahora es visible para otros que buscan "
            "**{crop}** en **{region}**. "
            "Ahora hay **{count}** entradas para este cultivo en esta región."
        ),
        # Browse page
        "browse_title": "Explorar el Commons",
        "no_entries": "Aún no hay entradas. ¡Sé el primero en contribuir!",
        "filter_all": "Todos",
        "filter_status": "Estado",
        "entries_found": "**{count}** entradas encontradas",
        "download_csv": "⬇️ Descargar como CSV",
    },
}

if "language" not in st.session_state:
    st.session_state["language"] = "English"

_lcol1, _lcol2 = st.sidebar.columns(2)
_active = st.session_state["language"]
if _lcol1.button("✓ ENG" if _active == "English" else "ENG"):
    st.session_state["language"] = "English"
    st.rerun()
if _lcol2.button("✓ ESP" if _active == "Español" else "ESP"):
    st.session_state["language"] = "Español"
    st.rerun()

t = TRANSLATIONS[st.session_state["language"]]

page = st.sidebar.radio(
    "Navegación",
    [t["calendar"], t["contribute"], t["browse"]],
)

if page == t["calendar"]:
    render_calendar_page(t)

elif page == t["contribute"]:
    render_contribute_page(t)

elif page == t["browse"]:
    render_browse_page(t)
