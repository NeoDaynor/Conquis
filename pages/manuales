import streamlit as st

from ui_theme import apply_app_theme, render_hero


st.set_page_config(
    page_title="Club Lakonn - Manuales",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

data = st.session_state.get(
    "menu_placeholder",
    {
        "section": "Menu",
        "title": "Seccion disponible",
        "description": "Esta vista queda preparada para continuar la implementacion.",
    },
)

apply_app_theme(max_width=980)

render_hero(
    data.get("title", "Seccion disponible"),
    data.get("description", ""),
    eyebrow=data.get("section", "Menu"),
)

st.markdown(
    '<p class="muted-note">Ultima actualización Abril - 2026.</p>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Volver al menu", use_container_width=True):
        st.switch_page("pages/menu.py")
with col2:
    if st.button("Cerrar sesion", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user_info", None)
        st.switch_page("app.py")
