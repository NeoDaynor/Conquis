import streamlit as st
import json
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Acceso", layout="centered")

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

# --- PANTALLA DE LOGEO ---
if not st.session_state["authenticated"]:
    st.markdown("<h1 style='text-align: center; color: #0070C0;'>ACCESO CLUB LAKONN</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar", use_container_width=True)
        
        if submit:
            user_data = authenticate(user_input, pass_input)
            if user_data:
                st.session_state["authenticated"] = True
                st.session_state["user_info"] = user_data
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# --- PANTALLA DE SELECCIÓN (SOLO SI ESTÁ AUTENTICADO) ---
else:
    user = st.session_state["user_info"]
    st.sidebar.write(f"**Usuario:** {user['nombre']}")
    st.sidebar.write(f"**Cargo:** {user['cargo']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"<h3 style='text-align: center;'>Bienvenido {user['nombre']}. Seleccione Unidad</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        unidades = [
            {"nombre": "ORION", "id": "Orion"},
            {"nombre": "PUMAS", "id": "Pumas"},
            {"nombre": "LIDERES", "id": "Lideres"}
        ]
        
        for u in unidades:
            if st.button(u["nombre"], key=u["id"], use_container_width=True, type="secondary"):
                st.session_state["unidad_seleccionada"] = u["id"]
                try:
                    st.switch_page("pages/gestion.py")
                except Exception:
                    st.switch_page("gestion")
