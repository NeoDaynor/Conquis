import streamlit as st
import streamlit.components.v1 as components
from login import mostrar_login
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Club Lakonn - Menú", layout="wide", initial_sidebar_state="collapsed")

# Función para convertir imagen a base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# --- ESTADO INICIAL DE LA APP (INDEX) ---
if "entro_a_la_app" not in st.session_state:
    st.session_state["entro_a_la_app"] = False

if not st.session_state["entro_a_la_app"]:
    # Cargar imagen del LogoCuerda
    img_logo = get_base64('images/LogoCuerda.jpg')
    
    # Inyección del HTML de tu archivo index.html
    index_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <style>
            body, html {{ 
                margin: 0; padding: 0; height: 100vh; overflow: hidden; 
                display: flex; justify-content: center; align-items: center; 
                background-color: #0e1117; 
            }}
            .contenedor {{ position: relative; display: inline-block; }}
            .imagen-fondo {{ display: block; max-width: 100vw; max-height: 100vh; object-fit: contain; }}
            .boton-triangulo {{
                position: absolute;
                top: 30%; left: 30%; width: 40%; height: 40%;
                clip-path: polygon(50% 100%, 0 0, 100% 0);
                cursor: pointer;
                background: transparent;
                border: none; outline: none;
            }}
            .boton-triangulo:hover {{ background: rgba(255, 255, 255, 0.1); }}
        </style>
    </head>
    <body>
        <div class="contenedor">
            <img src="data:image/jpg;base64,{img_logo}" class="imagen-fondo">
            <button class="boton-triangulo" id="trigger"></button>
        </div>
        <script>
            const btn = document.getElementById('trigger');
            btn.addEventListener('click', () => {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: true}}, '*');
            }});
        </script>
    </body>
    </html>
    """
    
    # Renderizar el componente
    clic_detectado = components.html(index_html, height=1000)
    
    if clic_detectado:
        st.session_state["entro_a_la_app"] = True
        st.rerun()

# --- FLUJO DE AUTENTICACIÓN Y MENÚ ---
else:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        mostrar_login()
    else:
        user = st.session_state["user_info"]
        
        # Cargamos imágenes de fondo para el menú
        bin_pc = get_base64('images/fondopc.jpg')
        bin_mob = get_base64('images/fondocelu.webp')

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

        st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
        
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

        with st.sidebar:
            st.markdown(f"### 👤 {user['nombre']}")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["entro_a_la_app"] = False # Opcional: vuelve al index al cerrar sesión
                st.rerun()
