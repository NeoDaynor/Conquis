import streamlit as st

from login import mostrar_login
from ui_theme import apply_app_theme, render_hero


st.set_page_config(
    page_title="Login - Club Lakonn",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_app_theme(max_width=800)

if st.session_state.get("authenticated", False):
    st.switch_page("pages/menu.py")

render_hero(
    "Acceso al sistema",
    "Ingresa con tu cuenta para administrar el club y continuar con el flujo de trabajo desde cualquier dispositivo.",
    eyebrow="Inicio de sesion",
)

mostrar_login()
