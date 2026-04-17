import streamlit as st
from login import mostrar_login  # Importamos el nuevo archivo

st.set_page_config(page_title="Club Lakonn", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    mostrar_login()
else:
    # --- LÓGICA DEL MENÚ ---
    user = st.session_state["user_info"]
    st.sidebar.markdown(f"### 👤 {user['nombre']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Selector de unidad con el estilo de color unificado
    st.markdown('<div style="background-color: rgba(255,255,255,0.9); padding: 30px; border-radius: 20px; border: 1px solid #0070C0; text-align: center;">', unsafe_allow_html=True)
    st.markdown(f"<h4>Hola {user['nombre']}, selecciona una unidad:</h4>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    if c1.button("🪐 ORION", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Orion"
        st.switch_page("pages/gestion.py")
    if c2.button("🐆 PUMAS", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Pumas"
        st.switch_page("pages/gestion.py")
    if c3.button("🎖️ LIDERES", use_container_width=True):
        st.session_state["unidad_seleccionada"] = "Lideres"
        st.switch_page("pages/gestion.py")
    st.markdown('</div>', unsafe_allow_html=True)
