import streamlit as st
import json
import os
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Acceso", layout="wide")

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

# Inicialización de estados de sesión
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "unidad_seleccionada" not in st.session_state:
    st.session_state["unidad_seleccionada"] = None

# --- ENCABEZADO CON LOGO (ESQUINA SUPERIOR DERECHA) ---
col_t1, col_t2 = st.columns([8, 1])
with col_t2:
    try:
        logo = Image.open("images/LogoLakonn.png")
        st.image(logo, use_container_width=True)
    except Exception:
        st.caption("Logo no hallado")

# --- PANTALLA DE LOGEO ELEGANTE ---
if not st.session_state["authenticated"]:
    # Centrado del formulario
    _, center_col, _ = st.columns([1, 1.5, 1])
    
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align: center; background-color: #f0f2f6; padding: 30px; border-radius: 15px; border: 1px solid #0070C0;'>
                <h1 style='color: #0070C0; margin-bottom: 0;'>BIENVENIDO</h1>
                <p style='color: #555;'>Gestión de Conquistadores - Club Lakonn</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            user_input = st.text_input("Usuario", placeholder="Ingrese su usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
            
            if submit:
                user_data = authenticate(user_input, pass_input)
                if user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_data
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verifique e intente de nuevo.")

# --- PANTALLA DE SELECCIÓN (SOLO SI ESTÁ AUTENTICADO) ---
else:
    user = st.session_state["user_info"]
    
    # Sidebar con info del usuario
    st.sidebar.markdown(f"### 👤 {user['nombre']}")
    st.sidebar.info(f"**Cargo:** {user['cargo']}\n\n**Rol:** {user['rol']}")
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.rerun()

    # Cuerpo principal
    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"<h4 style='text-align: center;'>Hola {user['nombre']}, por favor selecciona una unidad para gestionar:</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

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
                try:
                    st.switch_page("pages/gestion.py")
                except Exception:
                    st.switch_page("gestion")
