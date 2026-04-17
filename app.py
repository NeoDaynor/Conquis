import streamlit as st
from login import mostrar_login
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Club Lakonn - Menú", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    mostrar_login()
else:
    user = st.session_state["user_info"]
    
    # --- CSS PARA LOOK ELEGANTE Y ADAPTATIVO ---
    # Cargamos el fondo de PC por defecto para el menú
    def get_base64(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    
    bin_pc = get_base64('images/fondopc.jpg')

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_pc}");
            background-attachment: fixed;
            background-size: cover;
        }}
        
        /* Contenedor de Bienvenida */
        .welcome-card {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 40px;
            border-radius: 20px;
            border: 1px solid #0070C0;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 30px;
        }}

        /* BOTONES PREMIUM (Solución al TypeError) */
        div.stButton > button {{
            background-color: white !important;
            color: #0070C0 !important;
            border: 2px solid #0070C0 !important;
            border-radius: 15px !important;
            height: 150px !important; /* Altura forzada por CSS */
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

        # Disposición de botones: 3 columnas en PC, se apilan en Celular
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🪐\n\nORION", key="btn_orion", use_container_width=True):
                st.session_state["unidad_seleccionada"] = "Orion"
                st.switch_page("pages/gestion.py")
        
        with col2:
            if st.button("🐆\n\nPUMAS", key="btn_pumas", use_container_width=True):
                st.session_state["unidad_seleccionada"] = "Pumas"
                st.switch_page("pages/gestion.py")
                
        with col3:
            if st.button("🎖️\n\nLIDERES", key="btn_lideres", use_container_width=True):
                st.session_state["unidad_seleccionada"] = "Lideres"
                st.switch_page("pages/gestion.py")

    # Botón de salida discreto en el sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user['nombre']}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
