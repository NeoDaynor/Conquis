import streamlit as st
import base64

# Configuración de página en modo ancho para aprovechar la PC
st.set_page_config(page_title="Menú - Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

# Seguridad: Redirigir si no hay sesión
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

user = st.session_state.get("user_info", {"nombre": "Usuario"})
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# CSS Avanzado para Interfaz Responsiva
st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* Fondo responsivo */
    [data-testid="stAppViewContainer"] {{
        background-attachment: fixed; 
        background-size: cover; 
        background-position: center;
    }}
    @media (min-width: 769px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    /* Ajuste del contenedor principal en PC */
    .main .block-container {{
        max-width: 1200px !important;
        padding-top: 2rem !important;
    }}

    /* Tarjeta de bienvenida */
    .welcome-card {{
        background-color: rgba(255, 255, 255, 0.9); 
        padding: 30px; 
        border-radius: 20px;
        border: 2px solid #0070C0; 
        text-align: center; 
        color: #1E293B;
        margin-bottom: 2rem;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }}
    @media (prefers-color-scheme: dark) {{
        .welcome-card {{ background-color: rgba(30, 41, 59, 0.9); color: #F1F5F9; }}
    }}

    /* Estilo de Botones del Menú - Tamaño Fijo para evitar deformación */
    div.stButton > button {{
        background-color: white !important; 
        color: #0070C0 !important;
        border: 2px solid #0070C0 !important; 
        border-radius: 20px !important;
        height: 180px !important; 
        width: 100% !important; 
        font-weight: bold !important;
        font-size: 1.5rem !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        transition: all 0.3s ease;
    }}
    
    div.stButton > button:hover {{
        background-color: #0070C0 !important; 
        color: white !important;
        transform: translateY(-5px);
        box-shadow: 0px 8px 20px rgba(0,112,192,0.4);
    }}

    /* Ajustes específicos para Celular */
    @media (max-width: 768px) {{
        div.stButton > button {{
            height: 120px !important;
            font-size: 1.2rem !important;
        }}
        .main .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px #000; margin-bottom: 30px;'>CLUB LAKONN</h1>", unsafe_allow_html=True)

# Layout adaptativo
_, col_center, _ = st.columns([0.1, 2, 0.1])

with col_center:
    st.markdown(f'<div class="welcome-card"><h2>Bienvenido, {user["nombre"]}</h2><p style="font-size: 1.2rem;">Selecciona tu unidad para continuar</p></div>', unsafe_allow_html=True)
    
    # Columnas de unidades
    col_u1, col_u2, col_u3 = st.columns(3)
    
    with col_u1:
        if st.button("🪐\nORION", key="btn_orion"):
            st.session_state["unidad_seleccionada"] = "Orion"
            st.switch_page("pages/amigo.py")
            
    with col_u2:
        if st.button("🐆\nPUMAS", key="btn_pumas"):
            st.session_state["unidad_seleccionada"] = "Pumas"
            st.switch_page("pages/amigo.py")
            
    with col_u3:
        if st.button("🎖️\nLIDERES", key="btn_lideres"):
            st.session_state["unidad_seleccionada"] = "Lideres"
            st.switch_page("pages/amigo.py")

# Barra lateral para utilidades
with st.sidebar:
    st.markdown(f"### 👤 {user['nombre']}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
