import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from ui_theme import apply_app_theme, render_hero

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sección 1: Datos Personales", layout="wide")

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

usuario_activo = st.session_state.get("user_info", {})
apply_app_theme(max_width=1100)

# --- CORRECCIÓN DE VISIBILIDAD (CSS) ---
st.markdown("""
    <style>
    /* Asegura que el texto ingresado sea negro y el fondo blanco */
    input, textarea, [data-baseweb="input"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    /* Etiquetas de los campos en blanco para contraste */
    label p {
        color: #ffffff !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_excel():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open("RequisitosConquistadores").worksheet("C_Amigo_DatosP")

# --- UI PRINCIPAL ---
render_hero("Sección 1", "Datos Personales y Médicos", eyebrow="Cuadernillo de Amigo")

with st.form("form_datos_personales"):
    st.subheader("I. IDENTIFICACIÓN")
    col1, col2 = st.columns(2)
    with col1:
        f_nom = st.text_input("Nombre completo", value=usuario_activo.get("nombre"))
        f_eda = st.number_input("Edad", min_value=10, max_value=20, step=1)
        f_gra = st.text_input("Grado / Año escolar")
        f_dir = st.text_input("Dirección")
        f_bar = st.text_input("Barrio")
        f_cp  = st.text_input("Código Postal")
        f_clu = st.text_input("Club", value="Lakonn")
        f_uni = st.text_input("Unidad")
    with col2:
        f_ciu = st.text_input("Ciudad")
        f_pro = st.text_input("Provincia")
        f_ema = st.text_input("Correo electrónico", value=usuario_activo.get("correo"))
        f_tel = st.text_input("Teléfono")
        f_con = st.text_input("Consejero de Unidad")
        f_igl = st.text_input("Iglesia")
        f_aso = st.text_input("Asociación / Misión")
        f_union = st.text_input("Unión")

    st.markdown("---")
    st.subheader("II. INFORMACIÓN MÉDICA")
    m1, m2, m3 = st.columns(3)
    with m1: f_sangre = st.selectbox("Tipo Sanguíneo", ["O", "A", "B", "AB", "No sé"])
    with m2: f_rh = st.radio("Factor RH", ["+", "-"], horizontal=True)
    with m3: f_tetano = st.radio("Vacuna Antitetánica", ["Sí", "No"], horizontal=True)
    
    st.write("**Sufro de:**")
    s1, s2, s3, s4, s5 = st.columns(5)
    f_dia = s1.checkbox("Diabetes")
    f_epi = s2.checkbox("Epilepsia")
    f_car = s3.checkbox("P. Cardíacos")
    f_hem = s4.checkbox("Hemofilia")
    f_asm = s5.checkbox("Asma / Bronquitis")
    
    f_ale = st.text_area("Alergias o condiciones adicionales:")

    if st.form_submit_button("💾 GUARDAR DATOS PERSONALES", use_container_width=True):
        try:
            with st.spinner("Sincronizando con el libro..."):
                hoja = conectar_excel()
                fila = [
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    usuario_activo.get("usuario"),
                    f_nom, f_eda, f_gra, f_dir, f_bar, f_cp, f_ciu, f_pro, f_ema, f_tel,
                    f_clu, f_uni, f_con, f_igl, f_aso, f_union,
                    f"{f_sangre} {f_rh}", f_tetano, str(f_dia), str(f_epi), 
                    str(f_car), str(f_hem), str(f_asm), f_ale
                ]
                hoja.append_row(fila)
                st.success("¡Datos guardados correctamente!")
                st.balloons()
        except Exception as e:
            st.error(f"Error al conectar: {e}")

# Botón de navegación lateral para el futuro
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Menú Principal"):
    st.switch_page("pages/menu.py")

st.info("Una vez guardes tus datos, avisa a tu instructor para pasar a la siguiente sección.")
