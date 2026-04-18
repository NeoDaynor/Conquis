import streamlit as st
import base64

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Menú - Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

# 2. SEGURIDAD
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

user = st.session_state.get("user_info", {"nombre": "Usuario"})
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# 3. CSS DE NUEVO ESTILO (Dashboard Profesional)
st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}

    /* Fondo Responsivo */
    [data-testid="stAppViewContainer"] {{
        background-attachment: fixed; background-size: cover; background-position: center;
    }}
    @media (min-width: 769px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}

    /* Contenedor Principal */
    .main .block-container {{
        max-width: 1100px !important;
        padding-top: 3rem !important;
    }}

    /* Título con Neón */
    .main-title {{
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        color: white;
        text-shadow: 0 0 20px rgba(0,112,192,0.8), 2px 2px 10px #000;
        margin-bottom: 0.5rem;
    }}

    /* Tarjeta de Bienvenida Superior */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
    }}

    /* ESTILO DE LAS TARJETAS DE UNIDAD */
    .card-container {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 25px;
        padding: 40px 20px;
        text-align: center;
        border: 2px solid #0070C0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    
    @media (prefers-color-scheme: dark) {{
        .card-container {{ background: rgba(30, 41, 59, 0.95); border-color: #38bdf8; }}
    }}

    .card-container:hover {{
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(0, 112, 192, 0.4);
    }}

    /* Botón Invisible sobre la Tarjeta */
    div.stButton > button {{
        background: #0070C0 !important;
        color: white !important;
        border-radius: 12px !important;
        width: 100% !important;
        height: 50px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border: none !important;
        margin-top: 20px;
    }}

    div.stButton > button:hover {{
        background: #005a9e !important;
    }}

    /* Iconos Grandes */
    .unit-icon {{ font-size: 4rem; margin-bottom: 10px; }}
    .unit-name {{ font-size: 1.8rem; font-weight: 700; color: #0070C0; }}
    @media (prefers-color-scheme: dark) {{ .unit-name {{ color: #38bdf8; }} }}

    </style>
    """, unsafe_allow_html=True
)

# 4. CONTENIDO VISUAL
st.markdown('<h1 class="main-title">CLUB LAKONN</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="welcome-banner"><h2>Bienvenido, {user["nombre"]}</h2><p>Panel de Gestión de Unidades</p></div>', unsafe_allow_html=True)

# 5. GRILLA DE UNIDADES
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
        <div class="card-container">
            <div class="unit-icon">🪐</div>
            <div class="unit-name">ORION</div>
            <p style='color: gray;'>Gestión de Requisitos</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ACCEDER", key="go_orion"):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/amigo.py")

with col2:
    st.markdown("""
        <div class="card-container">
            <div class="unit-icon">🐆</div>
            <div class="unit-name">PUMAS</div>
            <p style='color: gray;'>Gestión de Requisitos</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ACCEDER", key="go_pumas"):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/amigo.py")

with col3:
    st.markdown("""
        <div class="card-container">
            <div class="unit-icon">🎖️</div>
            <div class="unit-name">LIDERES</div>
            <p style='color: gray;'>Gestión de Requisitos</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ACCEDER", key="go_lideres"):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/amigo.py")

# 6. SIDEBAR
with st.sidebar:
    st.markdown(f"### 🛡️ Sesión Activa\n**{user['nombre']}**")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
