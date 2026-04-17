import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Inicio", layout="centered")

# --- 2. INTERFAZ PRINCIPAL (image_f66589.png) ---
st.markdown("<h1 style='text-align: center;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
st.write("---")
st.markdown("<h3 style='text-align: center;'>Seleccione su Unidad</h3>", unsafe_allow_html=True)

# Creamos columnas para centrar los botones
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Al hacer clic, guardamos la unidad en el estado de la sesión
    if st.button("🔵 ORION", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/gestion.py")

    if st.button("🟢 PUMAS", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/gestion.py")

    if st.button("🟡 LIDERES", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/gestion.py")

# Nota: Si el usuario entra directo, por defecto no hay unidad
if "unidad_seleccionada" not in st.session_state:
    st.session_state["unidad_seleccionada"] = None
