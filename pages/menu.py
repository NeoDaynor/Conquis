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

# 3. CSS PARA TRANSFORMAR BOTONES EN TARJETAS CLICABLES
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
        max-width: 1000px !important;
        padding-top: 2rem !important;
    }}

    .main-title {{
        font-size: 3.5rem; font-weight: 800; text-align: center; color: white;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.7); margin-bottom: 1rem;
    }}

    /* BANNER DE BIENVENIDA */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #0070C0;
        padding: 15px; border-radius: 15px; text-align: center; color: #1E293B;
        margin-bottom: 2.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    @media (prefers-color-scheme: dark) {{
        .welcome-banner {{ background: rgba(30, 41, 59, 0.95); color: white; border-color: #38bdf8; }}
    }}

    /* ESTILO DE BOTÓN-TARJETA (UNIFICADO) */
    div.stButton > button {{
        background-color: white !important;
        color: #0070C0 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 20px !important;
        height: 220px !important;
        width: 100% !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: pre-wrap !important; /* Permite saltos de línea para el icono */
        line-height: 1.5 !important;
    }}

    @media (prefers-color-scheme: dark) {{
        div.stButton > button {{
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            border-color: #334155 !important;
        }}
    }}

    div.stButton > button:hover {{
        transform: translateY(-5px) !important;
        border-color: #0070C0 !important;
        box-shadow: 0 10px 20px rgba(0, 112, 192, 0.2) !important;
        background-color: #f8fafc !important;
    }}
    
    /* Tamaño del icono y texto dentro del botón */
    div.stButton > button p {{
        font-size: 1.5rem !important;
    }}
    </style>
    """, unsafe_allow_html=True
)

# 4. CONTENIDO
st.markdown('<h1 class="main-title">CLUB LAKONN</h1>', unsafe_allow_html=True)

st.markdown(f'''
    <div class="welcome-banner">
        <h2 style="margin:0;">Bienvenido, {user["nombre"]}</h2>
        <p style="margin:0; opacity: 0.8;">Selecciona una unidad para acceder</p>
    </div>
''', unsafe_allow_html=True)

# 5. GRILLA DE BOTONES-TARJETA (Clicables en todo su cuerpo)
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    # Usamos saltos de línea \n para separar el icono del texto dentro del mismo botón
    if st.button("🪐\n\nORION", key="btn_orion"):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/amigo.py")

with col2:
    if st.button("🐆\n\nPUMAS", key="btn_pumas"):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/amigo.py")

with col3:
    if st.button("🎖️\n\nLIDERES", key="btn_lideres"):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/amigo.py")

# 6. SIDEBAR
with st.sidebar:
    st.markdown(f"### 👤 Usuario\n**{user['nombre']}**")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
