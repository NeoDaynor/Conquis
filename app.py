import streamlit as st
import base64
from login import mostrar_login

# 1. CONFIGURACIÓN (Debe ser lo primero)
st.set_page_config(page_title="Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# 2. INICIALIZACIÓN DE ESTADOS (Persistencia)
if "vista" not in st.session_state:
    st.session_state["vista"] = "inicio"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- FUNCIÓN: PANTALLA DE INICIO ---
def pantalla_inicio():
    img_logo = get_base64('images/LogoCuerda.jpg')
    
    # CSS para forzar la imagen a cubrir todo y ocultar la interfaz de Streamlit
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-color: #0e1117;
        }}
        .main-container {{
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            display: flex; justify-content: center; align-items: center;
            z-index: 10;
        }}
        .img-fondo {{
            max-width: 100%; max-height: 100%; object-fit: contain;
        }}
        /* Estilo para el botón de Streamlit que haremos invisible pero grande */
        .stButton>button {{
            position: fixed;
            top: 30%; left: 30%; width: 40%; height: 40%;
            opacity: 0 !important;
            z-index: 20;
            cursor: pointer;
        }}
        #MainMenu, footer, header {{visibility: hidden;}}
        </style>
        <div class="main-container">
            <img src="data:image/jpg;base64,{img_logo}" class="img-fondo">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Este botón está "encima" del triángulo gracias al CSS de arriba
    if st.button("ENTRAR", key="triangulo_clic"):
        st.session_state["vista"] = "login"
        st.rerun()

# --- FUNCIÓN: MENÚ PRINCIPAL ---
def pantalla_menu():
    user = st.session_state.get("user_info", {"nombre": "Usuario"})
    bin_pc = get_base64('images/fondopc.jpg')
    bin_mob = get_base64('images/fondocelu.webp')

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_pc}");
            background-size: cover; background-attachment: fixed;
        }}
        @media (max-width: 768px) {{
            .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }}
        }}
        .welcome-card {{
            background-color: rgba(255, 255, 255, 0.9); padding: 30px;
            border-radius: 15px; border: 2px solid #0070C0; text-align: center;
        }}
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align:center; color:white;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🪐 ORION", use_container_width=True):
            st.session_state["unidad_seleccionada"] = "Orion"
            st.switch_page("pages/amigo.py")
    with col2:
        if st.button("🐆 PUMAS", use_container_width=True):
            st.session_state["unidad_seleccionada"] = "Pumas"
            st.switch_page("pages/amigo.py")
    with col3:
        if st.button("🎖️ LIDERES", use_container_width=True):
            st.session_state["unidad_seleccionada"] = "Lideres"
            st.switch_page("pages/amigo.py")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.session_state["vista"] = "inicio"
        st.rerun()

# --- LÓGICA DE ENRUTAMIENTO ---
if st.session_state["vista"] == "inicio":
    pantalla_inicio()
elif st.session_state["vista"] == "login":
    if not st.session_state["authenticated"]:
        mostrar_login()
        # El botón de "Entrar" dentro de mostrar_login debe poner authenticated=True
    else:
        st.session_state["vista"] = "menu"
        st.rerun()
elif st.session_state["vista"] == "menu":
    if not st.session_state["authenticated"]:
        st.session_state["vista"] = "login"
        st.rerun()
    pantalla_menu()
