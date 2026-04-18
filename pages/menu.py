import streamlit as st
import base64

# 1. CONFIGURACIÓN DE PÁGINA
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

# 3. CSS REFINADO (Equilibrio de tamaño y legibilidad)
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

    /* Contenedor Principal limitado para que no se desparrame en PC */
    .main .block-container {{
        max-width: 1000px !important;
        padding-top: 2rem !important;
    }}

    /* Título Superior */
    .main-title {{
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        color: white;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.7);
        margin-bottom: 1rem;
    }}

    /* BANNER DE BIENVENIDA (Corregido para legibilidad) */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.95); /* Opacidad alta para leer bien el nombre */
        border: 2px solid #0070C0;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        color: #1E293B;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    @media (prefers-color-scheme: dark) {{
        .welcome-banner {{ background: rgba(30, 41, 59, 0.95); color: white; border-color: #38bdf8; }}
    }}

    /* TARJETAS DE UNIDAD (Tamaño ajustado) */
    .card-container {{
        background: white;
        border-radius: 20px;
        padding: 25px 15px;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    @media (prefers-color-scheme: dark) {{
        .card-container {{ background: #1e293b; border-color: #334155; }}
    }}

    .card-container:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 112, 192, 0.2);
        border-color: #0070C0;
    }}

    /* Iconos y Nombres */
    .unit-icon {{ font-size: 3rem; margin-bottom: 5px; }}
    .unit-name {{ font-size: 1.5rem; font-weight: 700; color: #0070C0; }}
    @media (prefers-color-scheme: dark) {{ .unit-name {{ color: #38bdf8; }} }}

    /* Botón de Streamlit dentro de la tarjeta */
    div.stButton > button {{
        background: #0070C0 !important;
        color: white !important;
        border-radius: 10px !important;
        width: 100% !important;
        height: 45px !important;
        font-weight: bold !important;
        border: none !important;
        margin-top: 15px;
    }}
    </style>
    """, unsafe_allow_html=True
)

# 4. CONTENIDO
st.markdown('<h1 class="main-title">CLUB LAKONN</h1>', unsafe_allow_html=True)

# Banner de bienvenida con alta opacidad para lectura clara
st.markdown(f'''
    <div class="welcome-banner">
        <h2 style="margin:0;">Bienvenido, {user["nombre"]}</h2>
        <p style="margin:0; opacity: 0.8;">Selecciona una unidad para gestionar los requisitos</p>
    </div>
''', unsafe_allow_html=True)

# 5. FILA DE TARJETAS (3 columnas equilibradas)
col1, col2, col3 = st.columns(3, gap="medium")
                    
with col1:
    st.markdown("""
        <div class="card-container">
            <div class="unit-icon">🪐</div>
            <div class="unit-name">ORION</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ENTRAR", key="go_orion"):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/amigo.py")

with col2:
    st.markdown("""
        <div class="card-container">
            <div class="unit-icon">🐆</div>
            <div class="unit-name">PUMAS</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ENTRAR", key="go_pumas"):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/amigo.py")

with col3:
    st.markdown("""
        <div class="card-container">
            <div class="unit-icon">🎖️</div>
            <div class="unit-name">LIDERES</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ENTRAR", key="go_lideres"):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/amigo.py")

# 6. SIDEBAR
with st.sidebar:
    st.markdown(f"### 👤 Usuario\n**{user['nombre']}**")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
