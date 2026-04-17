import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Inicio", layout="centered")

# --- TÍTULO Y ESTILO ---
st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
st.write("---")
st.markdown("<h3 style='text-align: center;'>Seleccione su Unidad</h3>", unsafe_allow_html=True)

# --- SELECTOR DE UNIDAD ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    unidades = [
        {"nombre": "ORION", "id": "Orion"},
        {"nombre": "PUMAS", "id": "Pumas"},
        {"nombre": "LIDERES", "id": "Lideres"}
    ]
    
    for u in unidades:
        if st.button(u["nombre"], use_container_width=True):
            st.session_state["unidad_seleccionada"] = u["id"]
            # Navegación forzada al nombre del archivo dentro de /pages
            st.switch_page("pages/gestion.py")

# Inicialización de estado si no existe
if "unidad_seleccionada" not in st.session_state:
    st.session_state["unidad_seleccionada"] = None
