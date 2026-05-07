import streamlit as st
import base64
import time

st.set_page_config(page_title="Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

img_logo = get_base64('images/LogoCuerda.jpg')

# Muestra la imagen a pantalla completa (sin el botón invisible)
st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-color: #0e1117; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .portada {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        display: flex; justify-content: center; align-items: center;
    }}
    </style>
    <div class="portada">
        <img src="data:image/jpg;base64,{img_logo}" style="max-width:100%; max-height:100%; object-fit: contain;">
    </div>
    """, unsafe_allow_html=True
)

# Pausa la ejecución del script por 2 segundos
time.sleep(2)

# Redirige automáticamente a la página de login
st.switch_page("pages/login_page.py")
