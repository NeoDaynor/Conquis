import streamlit as st
import json
import os
from PIL import Image
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Acceso", layout="wide")

# --- FUNCIÓN PARA CARGAR IMAGEN LOCAL COMO FONDO ---
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

            /* Dispositivos Grandes (PC) */
            @media (min-width: 769px) {{
                .stApp {{
                    background-image: url("data:image/fondopc.jpg;base64,{bin_str_pc}");
                }}
            }}

            /* Dispositivos Pequeños (Celular) */
            @media (max-width: 768px) {{
                .stApp {{
                    background-image: url("data:image/fondocelu.webp;base64,{bin_str_mob}");
                }}
            }}

            .login-card {{
                text-align: center; 
                background-color: rgba(255, 255, 255, 0.9); 
                padding: 30px; 
                border-radius: 15px; 
                border: 1px solid #0070C0;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        # Si las imágenes no existen aún, mantiene el fondo oscuro por defecto
        st.markdown("<style>.stApp {background-color: #0e1117;}</style>", unsafe_allow_html=True)

# Aplicar fondos usando las rutas locales de tu carpeta images
set_bg_local('images/fondopc.jpg', 'images/fondocelu.webp')

# --- FUNCIONES DE AUTENTICACIÓN ---
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
if "unidad_seleccionada" not in st.session_state:
    st.session_state["unidad_seleccionada"] = None

# --- ENCABEZADO CON LOGO ---
col_t1, col_t2 = st.columns([8, 1])
with col_t2:
    try:
        logo = Image.open("images/LogoLakonn.png")
        st.image(logo, use_container_width=True)
    except Exception:
        pass

# --- PANTALLA DE LOGEO ---
if not st.session_state["authenticated"]:
    _, center_col, _ = st.columns([1, 1.5, 1])
    
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="login-card">
                <h1 style='color: #0070C0; margin-bottom: 0;'>BIENVENIDO</h1>
                <p style='color: #555;'>Gestión de Conquistadores - Club Lakonn</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            user_input = st.text_input("Usuario", placeholder="Usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Contraseña")
            submit = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
            
            if submit:
                user_data = authenticate(user_input, pass_input)
                if user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_data
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

# --- PANTALLA DE SELECCIÓN ---
else:
    user = st.session_state["user_info"]
    st.sidebar.markdown(f"### 👤 {user['nombre']}")
    st.sidebar.info(f"**Cargo:** {user['cargo']}")
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"<h4 style='text-align: center;'>Hola {user['nombre']}, selecciona una unidad:</h4>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        unidades = [
            {"nombre": "🪐 UNIDAD ORION", "id": "Orion"},
            {"nombre": "🐆 UNIDAD PUMAS", "id": "Pumas"},
            {"nombre": "🎖️ UNIDAD LIDERES", "id": "Lideres"}
        ]
        for u in unidades:
            if st.button(u["nombre"], key=u["id"], use_container_width=True, type="secondary"):
                st.session_state["unidad_seleccionada"] = u["id"]
                st.switch_page("pages/gestion.py")
