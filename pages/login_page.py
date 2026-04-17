import streamlit as st
import base64
from login import mostrar_login

st.set_page_config(page_title="Login - Club Lakonn", layout="centered", initial_sidebar_state="collapsed")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# Fondo responsivo y temas
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{
        background-attachment: fixed; background-size: cover; background-position: center;
    }}
    @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    </style>
    """, unsafe_allow_html=True
)

if st.session_state.get("authenticated", False):
    st.switch_page("pages/menu.py")

if st.button("⬅️ VOLVER AL INICIO"):
    st.switch_page("app.py")

mostrar_login()
