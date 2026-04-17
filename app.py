import streamlit as st
import base64
from login import mostrar_login

# 1. CONFIGURACIÓN (Debe ser lo primero)
st.set_page_config(page_title="Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# 2. GESTIÓN DE ESTADOS (Persistencia real)
if "vista" not in st.session_state:
    st.session_state["vista"] = "inicio"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- VISTA 1: PANTALLA DE INICIO (LogoCuerda) ---
if st.session_state["vista"] == "inicio":
    img_logo = get_base64('images/LogoCuerda.jpg')
    
    # CSS para la portada
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: #0e1117; }}
        #MainMenu, footer, header {{visibility: hidden;}}
        .portada-container {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            display: flex; justify-content: center; align-items: center;
            z-index: 1;
        }}
        .img-logo {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
        
        /* Estilo del botón de entrada (Triángulo) */
        .stButton>button {{
            position: fixed; top: 41%; left: 41%; width: 21%; height: 29%;
            background: transparent !important; color: transparent !important;
            border: none !important; z-index: 10; cursor: pointer;
            clip-path: polygon(43% 80%, 0 0, 80% 0);
        }}
        .stButton>button:hover {{ background: rgba(255,255,255,0.1) !important; }}
        </style>
        <div class="portada-container">
            <img src="data:image/jpg;base64,{img_logo}" class="img-logo">
        </div>
        """, unsafe_allow_html=True
    )
    
    if st.button(" ", key="btn_triangulo"):
        st.session_state["vista"] = "login"
        st.rerun()

# --- VISTA 2: LOGIN ---
elif st.session_state["vista"] == "login":
    if st.session_state["authenticated"]:
        st.session_state["vista"] = "menu"
        st.rerun()
    else:
        mostrar_login()

# --- VISTA 3: MENÚ PRINCIPAL ---
elif st.session_state["vista"] == "menu":
    if not st.session_state["authenticated"]:
        st.session_state["vista"] = "login"
        st.rerun()
    
    user = st.session_state.get("user_info", {"nombre": "Usuario"})
    bin_pc = get_base64('images/fondopc.jpg')
    bin_mob = get_base64('images/fondocelu.webp')

    # CSS del Menú (Restauramos tus botones y tarjetas)
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
            background-color: rgba(255, 255, 255, 0.9); padding: 40px; border-radius: 20px;
            border: 1px solid #0070C0; box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            text-align: center; margin-bottom: 30px;
        }}
        div.stButton > button {{
            background-color: white !important; color: #0070C0 !important;
            border: 2px solid #0070C0 !important; border-radius: 15px !important;
            height: 150px !important; width: 100% !important;
            font-size: 1.2em !important; font-weight: bold !important;
            display: flex; align-items: center; justify-content: center; flex-direction: column;
        }}
        div.stButton > button:hover {{
            background-color: #0070C0 !important; color: white !important;
            transform: translateY(-5px); box-shadow: 0px 8px 20px rgba(0,112,192,0.4);
        }}
        </style>
        <h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>CLUB LAKONN</h1>
        """, unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(f'<div class="welcome-card"><h2 style="color: #0070C0; margin:0;">Bienvenido, {user["nombre"]}</h2></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
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

    with st.sidebar:
        if st.button("🚪 Cerrar Sesión"):
            st.session_state["authenticated"] = False
            st.session_state["vista"] = "inicio"
            st.rerun()
