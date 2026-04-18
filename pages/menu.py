import streamlit as st
import base64

# Configuración de página: 'wide' es indispensable
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

# CSS DEFINITIVO PARA PROPORCIÓN
st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* 1. Fondo responsivo */
    [data-testid="stAppViewContainer"] {{
        background-attachment: fixed; 
        background-size: cover; 
        background-position: center;
    }}
    @media (min-width: 769px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ [data-testid="stAppViewContainer"] {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    /* 2. FORZAR EXPANSIÓN DEL CONTENEDOR EN PC */
    /* Esto quita los márgenes blancos gigantes a los lados en el PC */
    .main .block-container {{
        max-width: 95% !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}

    /* 3. Tarjeta de bienvenida proporcional */
    .welcome-card {{
        background-color: rgba(255, 255, 255, 0.9); 
        padding: 25px; 
        border-radius: 20px;
        border: 2px solid #0070C0; 
        text-align: center; 
        color: #1E293B;
        margin: 0 auto 3rem auto;
        max-width: 800px; /* Centramos la tarjeta pero dejamos que los botones se expandan más */
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }}

    /* 4. BOTONES GRANDES Y PROPORCIONADOS */
    div.stButton > button {{
        background-color: white !important; 
        color: #0070C0 !important;
        border: 2px solid #0070C0 !important; 
        border-radius: 20px !important;
        height: 250px !important; /* Aumentamos la altura en PC */
        width: 100% !important; 
        font-weight: bold !important;
        font-size: 2rem !important; /* Texto mucho más grande */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}
    
    div.stButton > button:hover {{
        background-color: #0070C0 !important; 
        color: white !important;
        transform: scale(1.02);
        transition: all 0.2s ease-in-out;
    }}

    /* 5. Ajustes para Celular (para que no se rompa) */
    @media (max-width: 768px) {{
        div.stButton > button {{
            height: 140px !important;
            font-size: 1.3rem !important;
        }}
        .main .block-container {{
            max-width: 100% !important;
            padding: 1rem !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True
)

# Título Superior
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 3px 3px 12px #000; font-size: 4rem; margin-top: 0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)

# Contenedor de Bienvenida
st.markdown(f'<div class="welcome-card"><h1>Bienvenido, {user["nombre"]}</h1><p style="font-size: 1.5rem;">Selecciona tu unidad para continuar</p></div>', unsafe_allow_html=True)

# FILA DE BOTONES: Usamos columnas con poco margen entre ellas para que se vean grandes
# En PC esto se verá como 3 tarjetas gigantes
col_u1, col_gap1, col_u2, col_gap2, col_u3 = st.columns([1, 0.1, 1, 0.1, 1])

with col_u1:
    if st.button("🪐\n\nORION", key="btn_orion"):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/amigo.py")
        
with col_u2:
    if st.button("🐆\n\nPUMAS", key="btn_pumas"):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/amigo.py")
        
with col_u3:
    if st.button("🎖️\n\nLIDERES", key="btn_lideres"):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/amigo.py")

# Barra lateral
with st.sidebar:
    st.markdown(f"### 👤 {user['nombre']}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
