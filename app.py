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
with _lcol1:
    st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
    if st.button("✓ ENG" if _active == "English" else "ENG", use_container_width=True):
        st.session_state["language"] = "English"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with _lcol2:
    st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
    if st.button("✓ ESP" if _active == "Español" else "ESP", use_container_width=True):
        st.session_state["language"] = "Español"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

t = TRANSLATIONS[st.session_state["language"]]

NAV_OPTIONS = ["Home", t["calendar"], t["contribute"], t["browse"]]

page = st.sidebar.radio(
    "Navegación",
    NAV_OPTIONS,
    index=NAV_OPTIONS.index(st.session_state.get("page", "Home")),
)
st.session_state["page"] = page

# ── Home / Landing ───────────────────────────────────────────────────────────
if page == "Home":
    PILLAR_STYLE = (
        "background-color:#fffdf7;"
        "border:1px solid #e8e0d0;"
        "border-radius:12px;"
        "padding:1.4rem 1.2rem;"
        "text-align:center;"
        "box-shadow:0 2px 6px rgba(0,0,0,0.05);"
        "height:100%;"
    )
    STEP_STYLE = "text-align:center;padding:1rem 0.5rem;"

    # Hero
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem 2rem;">
            <h1 style="font-size:3.2rem;color:#4a7c59;margin-bottom:0.4rem;">EDEN Commons</h1>
            <p style="font-size:1.25rem;color:#6b7c5a;margin-bottom:2rem;">
                Agricultural wisdom, from the ground up.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, cta_col, _ = st.columns([2, 1, 2])
    with cta_col:
        if st.button("🌱 Get Started", use_container_width=True):
            st.session_state["page"] = t["calendar"]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Three pillars
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(
            f'<div style="{PILLAR_STYLE}">'
            '<div style="font-size:2rem;">🌤️</div>'
            '<h3 style="color:#4a7c59;margin:0.5rem 0 0.4rem;">Climate Data</h3>'
            '<p style="color:#555;margin:0;">Real temperature and precipitation data for any location worldwide.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            f'<div style="{PILLAR_STYLE}">'
            '<div style="font-size:2rem;">🌙</div>'
            '<h3 style="color:#4a7c59;margin:0.5rem 0 0.4rem;">Lunar Cycles</h3>'
            '<p style="color:#555;margin:0;">Traditional moon phase timing from almanac wisdom.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            f'<div style="{PILLAR_STYLE}">'
            '<div style="font-size:2rem;">👥</div>'
            '<h3 style="color:#4a7c59;margin:0.5rem 0 0.4rem;">Community Knowledge</h3>'
            '<p style="color:#555;margin:0;">Farming practices shared by people from their land.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown(
        '<h2 style="text-align:center;color:#4a7c59;">How it works</h2>',
        unsafe_allow_html=True,
    )
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f'<div style="{STEP_STYLE}">'
            '<div style="font-size:2rem;">1️⃣</div>'
            '<p style="color:#2c2c1e;margin:0.4rem 0 0;">Enter your location and crop</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f'<div style="{STEP_STYLE}">'
            '<div style="font-size:2rem;">2️⃣</div>'
            '<p style="color:#2c2c1e;margin:0.4rem 0 0;">Get your personalized 12-month calendar</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f'<div style="{STEP_STYLE}">'
            '<div style="font-size:2rem;">3️⃣</div>'
            '<p style="color:#2c2c1e;margin:0.4rem 0 0;">Contribute what you know</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Call to action
    st.markdown(
        '<div style="text-align:center;padding:2rem 1rem;">'
        '<p style="font-size:1.1rem;color:#4a7c59;font-style:italic;margin-bottom:1.2rem;">'
        'Software for sovereignty. The knowledge belongs to the people who share it.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    _, cta2_col, _ = st.columns([2, 1, 2])
    with cta2_col:
        if st.button("Start your calendar →", use_container_width=True):
            st.session_state["page"] = t["calendar"]
            st.rerun()

# ── Main pages ───────────────────────────────────────────────────────────────
elif page == t["calendar"]:
    render_calendar_page(t)

elif page == t["contribute"]:
    render_contribute_page(t)

elif page == t["browse"]:
    render_browse_page(t)
