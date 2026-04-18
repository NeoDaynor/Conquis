import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Gestión", layout="wide", initial_sidebar_state="collapsed")

# Seguridad: Redirigir si no hay sesión o si no es admin
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

# --- 2. LÓGICA DE FONDO Y ESTILOS (Tu regla de diseño) ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
    .stApp {{
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}
    @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    /* Contenedor para el panel de administración */
    .admin-card {{
        background-color: rgba(224, 240, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #0070C0;
    }}
    </style>
    """, 
    unsafe_allow_html=True
)

# --- 3. LÓGICA DE DATOS ---
DB_PATH = 'users.json'

def cargar_datos():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": []}

def guardar_datos(datos):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- 4. NAVEGACIÓN (BARRA LATERAL) ---
with st.sidebar:
    st.title("⚙️ Administración")
    if st.button("⬅️ Volver al Menú", use_container_width=True):
        st.switch_page("menu.py") # Asegúrate de que este sea el nombre de tu archivo principal
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")

# --- 5. CONTENIDO DE GESTIÓN ---
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>GESTIÓN DE USUARIOS</h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.session_state.data = cargar_datos()

# Formulario para nuevo usuario
with st.expander("➕ Registrar Nuevo Miembro"):
    with st.form("nuevo_user"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo")
        cargo = c1.text_input("Cargo")
        usuario = c2.text_input("Usuario")
        password = c2.text_input("Password", type="password")
        rol = c2.selectbox("Rol", ["admin", "user"])
        if st.form_submit_button("Registrar"):
            ids = [u['id'] for u in st.session_state.data['users']]
            nuevo_user = {
                "id": max(ids, default=0) + 1,
                "nombre": nombre, "cargo": cargo, "rol": rol,
                "usuario": usuario, "password": password
            }
            st.session_state.data['users'].append(nuevo_user)
            guardar_datos(st.session_state.data)
            st.success("Usuario registrado localmente")
            st.rerun()

st.write("")

# Listado y edición
for i, user in enumerate(st.session_state.data['users']):
    with st.container():
        # Usamos una caja blanca para que los inputs sean legibles sobre el fondo
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 0.5])
        
        nuevo_nom = col1.text_input("Nombre", user['nombre'], key=f"n_{i}")
        nuevo_car = col2.text_input("Cargo", user['cargo'], key=f"c_{i}")
        nuevo_usu = col3.text_input("User", user['usuario'], key=f"u_{i}")
        nuevo_rol = col4.selectbox("Rol", ["admin", "user"], index=0 if user['rol']=="admin" else 1, key=f"r_{i}")
        
        if col5.button("🗑️", key=f"del_{i}"):
            st.session_state.data['users'].pop(i)
            guardar_datos(st.session_state.data)
            st.rerun()
            
        # Detección de cambios
        if (nuevo_nom != user['nombre'] or nuevo_car != user['cargo'] or 
            nuevo_usu != user['usuario'] or nuevo_rol != user['rol']):
            st.session_state.data['users'][i].update({
                "nombre": nuevo_nom, "cargo": nuevo_car,
                "usuario": nuevo_usu, "rol": nuevo_rol
            })
            guardar_datos(st.session_state.data)
            st.toast("Cambio guardado")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
