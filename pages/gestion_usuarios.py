import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Usuarios - Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

# Seguridad: Solo Admins
if not st.session_state.get("authenticated", False) or st.session_state.get("user_info", {}).get("rol") != "admin":
    st.switch_page("app.py")

# --- 2. FUNCIONES DE APOYO ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": []}

def save_users(data):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# --- 3. ESTILOS CSS ---
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

    .main-container {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #0070C0;
    }}
    </style>
    """, 
    unsafe_allow_html=True
)

# --- 4. BARRA DE NAVEGACIÓN SIMPLE ---
col_back, col_spacer, col_logout = st.columns([1, 2, 1])

with col_back:
    if st.button("⬅️ Volver al Menú", use_container_width=True):
        st.switch_page("pages/menu.py")

with col_logout:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")

st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>GESTIÓN DE USUARIOS</h1>", unsafe_allow_html=True)

# --- 5. LÓGICA DE USUARIOS ---
data = load_users()

with st.expander("➕ Registrar Nuevo Miembro"):
    with st.form("new_user_form"):
        c1, c2 = st.columns(2)
        new_nombre = c1.text_input("Nombre Completo")
        new_cargo = c2.text_input("Cargo")
        new_user = c1.text_input("Usuario (Login)")
        new_pass = c2.text_input("Contraseña", type="password")
        new_rol = st.selectbox("Rol de Sistema", ["admin", "lider", "conqui"])
        
        if st.form_submit_button("Guardar Usuario"):
            new_id = max([u['id'] for u in data['users']], default=0) + 1
            data['users'].append({
                "id": new_id,
                "nombre": new_nombre,
                "cargo": new_cargo,
                "rol": new_rol,
                "usuario": new_user,
                "password": new_pass
            })
            save_users(data)
            st.success("Usuario creado")
            st.rerun()

st.divider()

# --- 6. TABLA DE EDICIÓN ---
for idx, user in enumerate(data['users']):
    with st.container():
        # Usamos una fila para cada usuario imitando tu captura
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1.5, 0.5])
        
        updated_nombre = c1.text_input("Nombre", value=user['nombre'], key=f"nom_{user['id']}")
        updated_cargo = c2.text_input("Cargo", value=user['cargo'], key=f"car_{user['id']}")
        updated_user = c3.text_input("User", value=user['usuario'], key=f"usr_{user['id']}")
        
        # Selectbox de rol con el valor actual
        roles = ["admin", "lider", "conqui"]
        default_role_idx = roles.index(user.get('rol', 'conqui'))
        updated_rol = c4.selectbox("Rol", roles, index=default_role_idx, key=f"rol_{user['id']}")
        
        if c5.button("🗑️", key=f"del_{user['id']}"):
            data['users'].pop(idx)
            save_users(data)
            st.rerun()
            
        # Si algo cambia, actualizamos el json
        if (updated_nombre != user['nombre'] or updated_cargo != user['cargo'] or 
            updated_user != user['usuario'] or updated_rol != user.get('rol')):
            data['users'][idx]['nombre'] = updated_nombre
            data['users'][idx]['cargo'] = updated_cargo
            data['users'][idx]['usuario'] = updated_user
            data['users'][idx]['rol'] = updated_rol
            save_users(data)
            st.toast(f"Actualizado: {updated_nombre}")
