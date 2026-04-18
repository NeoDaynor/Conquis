import streamlit as st
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Club Lakonn - Menú", layout="wide", initial_sidebar_state="collapsed")

# Seguridad: Redirigir si no hay sesión
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

# Función para convertir imagen a base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

user = st.session_state.get("user_info", {"nombre": "Usuario"})
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# --- ESTILOS CSS (Basados en tu código funcional) ---
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
    
    .welcome-card {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid #0070C0;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 30px;
    }}

    div.stButton > button {{
        background-color: white !important;
        color: #0070C0 !important;
        border: 2px solid #0070C0 !important;
        border-radius: 15px !important;
        height: 150px !important;
        width: 100% !important;
        font-size: 1.2em !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }}
    
    div.stButton > button:hover {{
        background-color: #0070C0 !important;
        color: white !important;
        transform: translateY(-5px);
        box-shadow: 0px 8px 20px rgba(0,112,192,0.4);
    }}
    </style>
    """, 
    unsafe_allow_html=True
)

# --- CONTENIDO ---
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>CLUB LAKONN</h1>", unsafe_allow_html=True)

# La clave del éxito: Proporción 1:2:1 para centrar y dar tamaño justo
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    st.markdown(
        f"""
        <div class="welcome-card">
            <h2 style='color: #0070C0; margin:0;'>Bienvenido, {user['nombre']}</h2>
            <p style='color: #333; font-size: 1.1em;'>Selecciona una unidad para gestionar:</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- PRIMERA FILA ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🪐\n\nORION", key="btn_orion", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/amigo.py")

with col2:
    if st.button("🐆\n\nPUMAS", key="btn_pumas", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/amigo.py")

with col3:
    if st.button("🎖️\n\nLIDERES", key="btn_lideres", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/amigo.py")

st.write("") # Espaciador vertical

# --- SEGUNDA FILA ---
col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🦅\n\nAGUILAS", key="btn_aguilas", use_container_width=True): # Key único
        st.session_state["unidad_seleccionada"] = "Aguilas"
        st.switch_page("pages/amigo.py")

with col5:
    if st.button("🦊\n\nZORROS", key="btn_zorros", use_container_width=True): # Key único
        st.session_state["unidad_seleccionada"] = "Zorros"
        st.switch_page("pages/amigo.py")

with col6:
    # Nota: st.link_button NO genera error de duplicidad con st.button, 
    # pero es buena práctica darle su propio key si usas uno.
    st.link_button("🌐\n\nSDA SYSTEMS", 
                   "https://sg.sdasystems.org/cms/login.php?lang=esp", 
                   use_container_width=True)
# Barra lateral
with st.sidebar:
    st.markdown(f"### 👤 {user['nombre']}")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
