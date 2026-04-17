import streamlit as st
import base64
from login import mostrar_login

# Configuración de página
st.set_page_config(page_title="Login - Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# Imágenes de fondo
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# CSS Correctivo para PC y Móvil
st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* Fondo responsivo aplicado al contenedor principal */
    [data-testid="stAppViewContainer"] {{
        background-attachment: fixed; 
        background-size: cover; 
        background-position: center;
    }}
    @media (min-width: 769px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    /* Ajuste del contenedor de login para que no se estire en PC */
    .main .block-container {{
        max-width: 500px !important;
        padding-top: 5rem;
    }}
    </style>
    """, unsafe_allow_html=True
)

# Lógica de redirección si ya está autenticado
if st.session_state.get("authenticated", False):
    st.switch_page("pages/menu.py")

# Botón para volver a la portada
if st.button("⬅️ VOLVER AL INICIO"):
    st.switch_page("app.py")

# Llamada a la función de login
mostrar_login()
