import streamlit as st
import json
import os
from PIL import Image
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Acceso", layout="wide")

# --- FUNCIÓN PARA CARGAR IMAGEN LOCAL ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg_local(main_bg, mobile_bg):
    try:
        bin_str_pc = get_base64_of_bin_file(main_bg)
        bin_str_mob = get_base64_of_bin_file(mobile_bg)
        
        st.markdown(
            f"""
            <style>
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .stAppDeployButton {{display:none;}}
            button[title="Manage app"] {{display: none;}}

            .stApp {{
                background-attachment: fixed;
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
            }}

            @media (min-width: 769px) {{
                .stApp {{
                    background-image: url("data:image/jpg;base64,{bin_str_pc}");
                }}
            }}

            @media (max-width: 768px) {{
                .stApp {{
                    background-image: url("data:image/webp;base64,{bin_str_mob}");
                }}
            }}

            /* ESTILO UNIFICADO PARA BIENVENIDA Y FORMULARIO */
            /* Aplicamos el fondo blanco al contenedor del formulario y al div superior */
            [data-testid="stForm"], .login-header {{
                background-color: rgba(255, 255, 255, 0.9) !important;
                border: 1px solid #0070C0 !important;
                padding: 30px !important;
                color: #1E1E1E !important;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            }}

            /* Redondeamos solo la parte superior del encabezado */
            .login-header {{
                border-radius: 20px 20px 0 0 !important;
                border-bottom: none !important;
                text-align: center;
                margin-top: 30px;
            }}

            /* Redondeamos solo la parte inferior del formulario */
            [data-testid="stForm"] {{
                border-radius: 0 0 20px 20px !important;
                margin-top: -1px; /* Para que no se vea doble borde entre piezas */
            }}

            /* Asegurar visibilidad de textos */
            .stMarkdown p, label, .stMarkdown h1, .stMarkdown h3 {{
                color: #1E1E1E !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.markdown("<style>.stApp {background-color: #0e1117;}</style>", unsafe_allow_html=True)

set_bg_local('images/fondopc.jpg', 'images/fondocelu.webp')

# --- LÓGICA DE USUARIOS ---
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)['users']
    return []

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['usuario'] == username and user['password'] == password:
            return user
    return None

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# --- LOGO ---
col_logo1, col_logo2 = st.columns([8, 1])
with col_logo2:
    try:
        st.image(Image.open("images/LogoLakonn.png"), use_container_width=True)
    except Exception:
        pass

# --- PANTALLA DE ACCESO ---
if not st.session_state["authenticated"]:
    _, center_col, _ = st.columns([1, 1.8, 1])
    
    with center_col:
        # PARTE 1: Encabezado de Bienvenido
        st.markdown(
            """
            <div class="login-header">
                <h1 style='color: #0070C0; margin-bottom: 0;'>BIENVENIDO</h1>
                <p style='color: #555;'>Gestión de Conquistadores - Club Lakonn</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # PARTE 2: Formulario con el mismo fondo (Configurado vía CSS)
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            user_input = st.text_input("Usuario", placeholder="Escriba su usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Escriba su contraseña")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
            
            if submit:
                user_data = authenticate(user_input, pass_input)
                if user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_data
                    st.rerun()
                else:
                    st.error("Error: Usuario o contraseña incorrectos.")

# --- MENÚ DE SELECCIÓN ---
else:
    user = st.session_state["user_info"]
    st.sidebar.markdown(f"### 👤 {user['nombre']}")
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Tarjeta de selección
    st.markdown('<div class="login-header" style="border-radius: 20px !important; border-bottom: 1px solid #0070C0 !important;">', unsafe_allow_html=True)
    st.markdown(f"<h4>Hola {user['nombre']}, selecciona una unidad:</h4>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    if c1.button("🪐 ORION", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/gestion.py")
    if c2.button("🐆 PUMAS", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/gestion.py")
    if c3.button("🎖️ LIDERES", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/gestion.py")
    st.markdown('</div>', unsafe_allow_html=True)
