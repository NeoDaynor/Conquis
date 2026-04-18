import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión - Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

# Seguridad: Redirigir si no hay sesión
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

# --- 2. LÓGICA DE FONDO Y ESTILOS (IGUAL AL LOGIN) ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* Fondo responsivo igual al Login */
    [data-testid="stAppViewContainer"] {{
        background-attachment: fixed; 
        background-size: cover; 
        background-position: center;
    }}
    @media (min-width: 769px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    /* EL DIV CON EL COLOR Y TRANSPARENCIA DEL LOGIN */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: rgba(255, 255, 255, 0.95) !important; /* Misma transparencia que el login */
        border-radius: 20px !important;
        border: 1px solid #0070C0 !important;
        padding: 25px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3) !important;
        margin-bottom: 20px !important;
    }}

    /* Ajuste de labels para que resalten */
    .stTextInput label, .stSelectbox label {{
        color: #0070C0 !important;
        font-weight: bold !important;
    }}
    </style>
    """, 
    unsafe_allow_html=True
)

# --- 3. NAVEGACIÓN (BARRA LATERAL) ---
with st.sidebar:
    st.markdown("### ⚙️ Navegación")
    if st.button("⬅️ Volver al Menú", use_container_width=True):
        st.switch_page("menu.py")
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")

# --- 4. LÓGICA DE DATOS ---
DB_PATH = 'users.json'

def cargar_datos():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": []}

def guardar_datos(datos):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

if 'data' not in st.session_state:
    st.session_state.data = cargar_datos()

# --- 5. CONTENIDO ---
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px #000;'>ADMINISTRACIÓN DE USUARIOS</h1>", unsafe_allow_html=True)

# Formulario para nuevo usuario (envuelto en el div estilizado)
with st.container(border=True):
    st.subheader("➕ Registrar Nuevo Miembro")
    with st.form("nuevo_user_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre Completo")
        c = c1.text_input("Cargo")
        u = c2.text_input("Usuario")
        p = c2.text_input("Password", type="password")
        r = c2.selectbox("Rol", ["admin", "user"])
        if st.form_submit_button("Registrar en Sistema"):
            if n and u and p:
                ids = [usr['id'] for usr in st.session_state.data['users']]
                nuevo = {"id": max(ids, default=0)+1, "nombre": n, "cargo": c, "rol": r, "usuario": u, "password": p, "correo": ""}
                st.session_state.data['users'].append(nuevo)
                guardar_datos(st.session_state.data)
                st.success(f"Usuario {n} registrado")
                st.rerun()
            else:
                st.error("Faltan campos obligatorios")

st.write("")

# Listado de usuarios existentes
for i, user in enumerate(st.session_state.data['users']):
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
            
        # Guardado automático de ediciones
        if (nuevo_nom != user['nombre'] or nuevo_car != user['cargo'] or 
            nuevo_usu != user['usuario'] or nuevo_rol != user['rol']):
            st.session_state.data['users'][i].update({
                "nombre": nuevo_nom, "cargo": nuevo_car,
                "usuario": nuevo_usu, "rol": nuevo_rol
            })
            guardar_datos(st.session_state.data)
            st.toast("Datos actualizados")
