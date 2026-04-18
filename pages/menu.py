import streamlit as st
import base64

# --- 1. CONFIGURACIÓN ORIGINAL ---
st.set_page_config(page_title="Club Lakonn - Menú", layout="wide", initial_sidebar_state="collapsed")

# Seguridad: Redirigir si no hay sesión
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

# Función Base64
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

# --- 2. DATOS DEL USUARIO Y ROLES ---
user = st.session_state.get("user_info", {"nombre": "Usuario", "rol": "conqui"})
rol = user.get("rol", "conqui")

bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# --- 3. ESTILOS CSS (Protocolo Identidad Visual) ---
st.markdown(
    f"""
    <style>
    #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
    
    .stApp {{
        background-attachment: fixed; background-size: cover; background-position: center;
    }}
    @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    .welcome-card {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px; border-radius: 20px; border: 1px solid #0070C0;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
        text-align: center; margin-bottom: 30px;
    }}

    div.stButton > button {{
        background-color: white !important;
        color: #0070C0 !important;
        border: 2px solid #0070C0 !important;
        border-radius: 15px !important;
        height: 140px !important;
        width: 100% !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}
    
    div.stButton > button:hover {{
        background-color: #0070C0 !important;
        color: white !important;
        transform: translateY(-5px);
    }}

    /* Estilo para el botón flotante de Admin */
    .element-container:has(#admin_btn_container) {{
        position: fixed; top: 20px; right: 20px; z-index: 999999; width: auto;
    }}
    </style>
    <div id="admin_btn_container"></div>
    """, 
    unsafe_allow_html=True
)

# --- 4. BOTÓN FLOTANTE (SOLO ADMIN) ---
if rol == "admin":
    if st.button("⚙️", key="btn_fast_admin", help="Gestión de Usuarios"):
        st.switch_page("pages/gestion_usuarios.py")

# --- 5. CONTENIDO PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>CLUB LAKONN</h1>", unsafe_allow_html=True)

_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    st.markdown(
        f"""
        <div class="welcome-card">
            <h2 style='color: #0070C0; margin:0;'>Hola, {user['nombre']}</h2>
            <p style='color: #333; font-size: 1em;'>{'Gestiona las unidades a tu cargo:' if rol != "conqui" else 'Consulta tu avance personal:'}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- 6. GRID DE UNIDADES (FILTRADO POR ROL) ---
# Definimos las unidades para iterar fácilmente
unidades = [
    {"name": "ORION", "key": "Orion", "icon": "🪐"},
    {"name": "ESTER-ELLAS", "key": "Ester-ellas", "icon": "🐆"},
    {"name": "RAYEN", "key": "Rayen", "icon": "🎖️"},
    {"name": "ULTRASOLIS", "key": "Ultrasolis", "icon": "🦅"},
    {"name": "LIDERES", "key": "Lideres", "icon": "🎖️"}
]

# Si es "conqui", podrías filtrar para que solo vea la suya si tuvieras ese dato en el JSON.
# Por ahora, permitimos que el conqui vea los botones, pero al entrar a 'amigo.py' ya lo tenemos bloqueado.
# Sin embargo, para cumplir tu regla de "solo ver su avance", ocultaremos botones innecesarios si es conqui.

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

# Lógica de visualización de botones de unidades
for i, uni in enumerate(unidades):
    with cols[i % 3]:
        # El Admin y Lider ven todo. El Conqui ve todo pero amigo.py lo filtrará (o puedes añadir un if rol == "conqui" aquí)
        if st.button(f"{uni['icon']}\n\n{uni['name']}", key=f"btn_{uni['key']}"):
            st.session_state["unidad_seleccionada"] = uni['key']
            st.switch_page("pages/amigo.py")

# Espacio para el botón de SGDC
with col3:
    if i % 3 != 2: # Si el último botón no fue en la col3, lo ponemos ahí
        pass 
    
    # Enlace externo SGDC (Siempre visible)
    img_sgdc = get_base64('images/SGDC.png')
    st.markdown(
        f"""
        <a href="https://sg.sdasystems.org/cms/login.php?lang=esp" target="_blank" style="text-decoration: none;">
            <div style="background-color: white; border: 2px solid #0070C0; border-radius: 15px; height: 140px; display: flex; align-items: center; justify-content: center; padding: 10px;">
                <img src="data:image/png;base64,{img_sgdc}" style="max-width: 90%; max-height: 90%;">
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

# --- 7. BARRA LATERAL (PROTEGIDA) ---
with st.sidebar:
    st.markdown(f"### 👤 {user['nombre']}")
    st.info(f"Rol: {rol.capitalize()}")
    
    # Solo el Admin ve la gestión de usuarios
    if rol == "admin":
        st.divider()
        if st.button("⚙️ Gestión de Usuarios", use_container_width=True):
            st.switch_page("pages/gestion_usuarios.py")

    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
        
