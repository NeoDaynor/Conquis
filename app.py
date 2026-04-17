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

            /* --- LA SOLUCIÓN AL FONDO DEL DIV --- */
            /* Forzamos que los contenedores de Streamlit sean transparentes */
            [data-testid="stForm"] {{
                background-color: transparent !important;
                border: none !important;
                padding: 0 !important;
            }}

            .login-card {{
                background-color: rgba(255, 255, 255, 0.9) !important; 
                padding: 40px; 
                border-radius: 20px; 
                border: 2px solid #0070C0;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
                margin-top: 30px;
                color: #1E1E1E !important;
            }}
            
            /* Aseguramos que los textos sean visibles sobre el blanco */
            .login-card h1, .login-card p, .login-card h3, .login-card label {{
                color: #1E1E1E !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.markdown("<style>.stApp {background-color: #0e1117;}</style>", unsafe_allow_html=True)

set_bg_local('images/fondopc.jpg', 'images/fondocelu.webp')

# --- LOGICA DE AUTENTICACIÓN ---
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

# --- LOGO SUPERIOR ---
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
        # Aquí inyectamos el DIV que ahora sí debería verse
        st.markdown(
            """
            <div class="login-card">
                <h1 style='color: #0070C0; text-align: center; margin-top: 0;'>BIENVENIDO</h1>
                <p style='text-align: center;'>Gestión de Conquistadores - Club Lakonn</p>
                <hr style='border: 0.5px solid #0070C0; margin-bottom: 20px;'>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # El formulario se superpone a la tarjeta pero es transparente
        with st.form("login_form", border=False):
            st.markdown("<h3 style='color: #1E1E1E;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
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
    st.sidebar.info(f"**Cargo:** {user['cargo']}")
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown('<div class="login-card" style="margin-top: 0; padding: 25px;">', unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>Hola {user['nombre']}, selecciona una unidad:</h4>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    unidades = [
        {"nombre": "🪐 ORION", "id": "Orion", "col": col_btn1},
        {"nombre": "🐆 PUMAS", "id": "Pumas", "col": col_btn2},
        {"nombre": "🎖️ LIDERES", "id": "Lideres", "col": col_btn3}
    ]
    
    for u in unidades:
        if u["col"].button(u["nombre"], key=u["id"], use_container_width=True):
            st.session_state["unidad_seleccionada"] = u["id"]
            st.switch_page("pages/gestion.py")
