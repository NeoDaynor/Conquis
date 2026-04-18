import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Gestión", layout="wide", initial_sidebar_state="collapsed")

# Seguridad
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

# --- 2. LÓGICA DE FONDO Y ESTILOS ---
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
        background-attachment: fixed; background-size: cover; background-position: center;
    }}
    @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    /* SOLUCIÓN AL DIV: Estilizamos el contenedor nativo de Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px;
        border: 1px solid #0070C0 !important;
        padding: 15px;
        margin-bottom: 10px;
    }}
    
    /* Estilo para los títulos de los inputs dentro de las cajas */
    .stTextInput label, .stSelectbox label {{
        color: #0070C0 !important;
        font-weight: bold !important;
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

# --- 4. NAVEGACIÓN ---
with st.sidebar:
    st.title("⚙️ Configuración")
    if st.button("⬅️ Volver al Menú", use_container_width=True):
        st.switch_page("menu.py")
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")

# --- 5. CONTENIDO ---
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>ADMINISTRACIÓN DE USUARIOS</h1>", unsafe_allow_html=True)

if 'data' not in st.session_state:
    st.session_state.data = cargar_datos()

# Registro de nuevo miembro
with st.expander("➕ Registrar Nuevo Miembro"):
    with st.form("nuevo_user_form"):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre Completo")
        c = c1.text_input("Cargo")
        u = c2.text_input("Usuario")
        p = c2.text_input("Password", type="password")
        r = c2.selectbox("Rol", ["admin", "user"])
        if st.form_submit_button("Guardar"):
            ids = [usr['id'] for usr in st.session_state.data['users']]
            nuevo = {"id": max(ids, default=0)+1, "nombre": n, "cargo": c, "rol": r, "usuario": u, "password": p, "correo": ""}
            st.session_state.data['users'].append(nuevo)
            guardar_datos(st.session_state.data)
            st.rerun()

st.write("")

# Listado de usuarios con ENVOLVIMIENTO REAL
for i, user in enumerate(st.session_state.data['users']):
    # st.container(border=True) ahora actúa como tu "admin-card"
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 0.5])
        
        nuevo_nom = col1.text_input("Nombre", user['nombre'], key=f"n_{i}")
        nuevo_car = col2.text_input("Cargo", user['cargo'], key=f"c_{i}")
        nuevo_usu = col3.text_input("User", user['usuario'], key=f"u_{i}")
        nuevo_rol = col4.selectbox("Rol", ["admin", "user"], index=0 if user['rol']=="admin" else 1, key=f"r_{i}")
        
        if col5.button("🗑️", key=f"del_{i}"):
            st.session_state.data['users'].pop(i)
            guardar_datos(st.session_state.data)
            st.rerun()
            
        # Actualización automática si hay cambios
        if (nuevo_nom != user['nombre'] or nuevo_car != user['cargo'] or 
            nuevo_usu != user['usuario'] or nuevo_rol != user['rol']):
            st.session_state.data['users'][i].update({
                "nombre": nuevo_nom, "cargo": nuevo_car,
                "usuario": nuevo_usu, "rol": nuevo_rol
            })
            guardar_datos(st.session_state.data)
            st.toast("Actualizado")
