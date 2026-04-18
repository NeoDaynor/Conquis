import streamlit as st
import base64

# --- CONFIGURACIÓN ---
# Cambiamos "collapsed" por "expanded" para que veas la barra lateral de inmediato
st.set_page_config(page_title="Club Lakonn - Menú", layout="wide", initial_sidebar_state="expanded")

# Seguridad: Redirigir si no hay sesión
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

# Función para convertir imagen a base64
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# Obtenemos info del usuario
user = st.session_state.get("user_info", {"nombre": "Usuario", "rol": "user"})
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# --- ESTILOS CSS ---
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

# --- CONTENIDO PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>CLUB LAKONN</h1>", unsafe_allow_html=True)

_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    st.markdown(f"""
        <div class="welcome-card">
            <h2 style='color: #0070C0; margin:0;'>Bienvenido, {user['nombre']}</h2>
            <p style='color: #333; font-size: 1.1em;'>Selecciona una unidad para gestionar:</p>
        </div>
        """, unsafe_allow_html=True)

# --- GRILLA DE BOTONES ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🪐\n\nORION", key="btn_orion"):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/amigo.py")
with col2:
    if st.button("🐆\n\nESTER-ELLAS", key="btn_pumas"):
        st.session_state["unidad_seleccionada"] = "Ester-ellas"
        st.switch_page("pages/amigo.py")
with col3:
    if st.button("🎖️\n\nRAYEN", key="btn_lideres"):
        st.session_state["unidad_seleccionada"] = "Rayen"
        st.switch_page("pages/amigo.py")

st.write("") 

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("🦅\n\nULTRASOLIS", key="btn_aguilas"):
        st.session_state["unidad_seleccionada"] = "Ultrasolis"
        st.switch_page("pages/amigo.py")
with col5:
    if st.button("🎖️\n\nLIDERES", key="btn_lideres_2"):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/amigo.py")
with col6:
    img_sgdc = get_base64('images/SGDC.png')
    st.markdown(f"""
        <a href="https://sg.sdasystems.org/cms/login.php?lang=esp" target="_blank" style="text-decoration: none;">
            <div style="background-color: white; border: 2px solid #0070C0; border-radius: 15px; height: 150px; width: 100%; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); padding: 10px;">
                <img src="data:image/png;base64,{img_sgdc}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
            </div>
        </a>
        """, unsafe_allow_html=True)

# --- BARRA LATERAL (AQUÍ ESTÁ LA MAGIA) ---
with st.sidebar:
    st.markdown(f"### 👤 {user['nombre']}")
    st.write(f"Rol actual: **{user.get('rol')}**")
    
    st.divider()

    # IMPORTANTE: Solo se muestra si el usuario logueado tiene rol "admin" en el JSON
    if user.get("rol") == "admin":
        st.subheader("Configuración")
        if st.button("⚙️ Gestión de Usuarios", use_container_width=True):
            st.switch_page("pages/gestion_usuarios.py")
    
    st.write("")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
