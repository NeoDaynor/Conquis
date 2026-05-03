import streamlit as st

from ui_theme import apply_app_theme, render_hero


st.set_page_config(
    page_title="Club Lakonn - Registro de Unidades",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")


def open_placeholder(section, title, description):
    st.session_state["menu_placeholder"] = {
        "section": section,
        "title": title,
        "description": description,
    }
    st.switch_page("pages/seccion.py")


nivel = st.session_state.get("nivel_tarjeta", "Amigo")
apply_app_theme(max_width=980)

# 1. Extraemos toda la información clave del usuario
user = st.session_state.get("user_info", {"nombre": "Usuario", "rol": "admin"})
es_conqui = user.get("rol") == "conqui"
unidad_del_conqui = user.get("unidad", "") # Extraemos el nuevo campo "unidad" del JSON

render_hero(
    f"Registro de Unidades - {nivel}",
    "Selecciona la unidad que deseas gestionar." if not es_conqui else "Accede a tu unidad para ver tu progreso.",
    eyebrow="Tarjetas progresivas",
    pills=[f"Hola de nuevo {user.get('nombre', '')}"
    ,f"Tu correo es {user.get('correo', '')}"
    ,f"Te desempeñas como: {user.get('rol', '').upper()}"
    ],
)

# 2. Lista maestra de unidades
units = ["Orion", "Ester-ellas", "Rayen", "Ultrasolis", "Lideres"]

# 3. FILTRO INTELIGENTE: Si es conquistador, reducimos la lista solo a su unidad
if es_conqui:
    units = [u for u in units if u == unidad_del_conqui]
    
    # Prevención de errores por si la unidad en el JSON está mal escrita
    if not units:
        st.warning(f"⚠️ Hola {user.get('nombre')}, tu unidad asignada ('{unidad_del_conqui}') no coincide con los registros del sistema. Consulta con tu consejero.")

st.markdown('<p class="section-label">Unidades disponibles</p>', unsafe_allow_html=True)

left_col, right_col = st.columns(2)

# 4. Dibujamos las tarjetas (se adapta automáticamente si es 1 o si son 5)
for index, unit in enumerate(units):
    target_col = left_col if index % 2 == 0 else right_col
    with target_col:
        if st.button(unit, key=f"unit_{unit}", use_container_width=True):
            st.session_state["unidad_seleccionada"] = unit
            if nivel == "Amigo":
                st.switch_page("pages/amigo.py")
            else:
                open_placeholder(
                    f"Tarjetas progresivas / {nivel}",
                    f"Registro de Unidades - {nivel}",
                    #f"La unidad {unit} ya quedo integrada en el flujo. Falta implementar la logica especifica de {nivel}.",
                )

st.markdown('</br> </br>', unsafe_allow_html=True)
footer_left, footer_right = st.columns(2)
with footer_left:
    if st.button("Volver al menu", key="back_menu", use_container_width=True):
        st.switch_page("pages/menu.py")
with footer_right:
    if st.button("Cerrar sesion", key="logout_units", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user_info", None)
        st.switch_page("app.py")
