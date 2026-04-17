import streamlit as st
from login import mostrar_login
from PIL import Image

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Club Lakonn - Menú", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    mostrar_login()
else:
    user = st.session_state["user_info"]
    
    # --- INTERFAZ DEL MENÚ ELEGANTE ---
    # Sidebar personalizada
    with st.sidebar:
        st.markdown(f"### 👤 {user['nombre']}")
        st.info(f"**Cargo:** {user['cargo']}")
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    # Título Principal con sombra para PC y Móvil
    st.markdown(
        """
        <h1 style='text-align: center; color: #0070C0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); font-size: 3em;'>
            CLUB LAKONN
        </h1>
        <p style='text-align: center; color: #555; font-size: 1.2em;'>Panel de Gestión de Unidades</p>
        <hr style='border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,112,192,0.75), rgba(0,0,0,0));'>
        """, 
        unsafe_allow_html=True
    )

    # Contenedor de Selección
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.markdown(
            f"""
            <div style="background-color: rgba(255, 255, 255, 0.9); 
                        padding: 30px; 
                        border-radius: 20px; 
                        border: 1px solid #0070C0; 
                        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
                        text-align: center;
                        margin-bottom: 20px;">
                <h4 style="color: #1E1E1E; margin-bottom: 25px;">Bienvenido, {user['nombre']}<br>
                <span style="font-size: 0.8em; font-weight: normal;">Selecciona una unidad para gestionar:</span></h4>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Botones de Unidades con estilo mejorado
        # Usamos columnas que en móvil Streamlit apila automáticamente
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🪐\n\nORION", key="btn_orion", use_container_width=True, height=150):
                st.session_state["unidad_seleccionada"] = "Orion"
                st.switch_page("pages/gestion.py")
        
        with col2:
            if st.button("🐆\n\nPUMAS", key="btn_pumas", use_container_width=True, height=150):
                st.session_state["unidad_seleccionada"] = "Pumas"
                st.switch_page("pages/gestion.py")
                
        with col3:
            if st.button("🎖️\n\nLIDERES", key="btn_lideres", use_container_width=True, height=150):
                st.session_state["unidad_seleccionada"] = "Lideres"
                st.switch_page("pages/gestion.py")

    # Estilo CSS adicional para que los botones del menú se vean premium
    st.markdown(
        """
        <style>
        /* Estilo para los botones de unidades */
        div.stButton > button {
            background-color: #ffffff !important;
            color: #0070C0 !important;
            border: 2px solid #0070C0 !important;
            border-radius: 15px !important;
            font-weight: bold !important;
            font-size: 1.1em !important;
            transition: all 0.3s ease !important;
            white-space: pre-wrap !important; /* Permite el salto de línea para el emoji */
        }
        
        div.stButton > button:hover {
            background-color: #0070C0 !important;
            color: white !important;
            transform: translateY(-5px) !important;
            box-shadow: 0px 5px 15px rgba(0,112,192,0.4) !important;
        }

        /* Ajustes para el texto en fondo semitransparente */
        .stMarkdown h4 {
            color: #1E1E1E !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
