import streamlit as st
import pandas as pd
import io
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Importamos tu tema visual
from ui_theme import apply_app_theme, render_hero

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cuadernillo Digital - Amigo", layout="wide")

# Verificación de autenticación
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

usuario_activo = st.session_state.get("user_info", {})
apply_app_theme(max_width=1100)

# --- INICIALIZACIÓN DE ESTADO DE NAVEGACIÓN ---
if "seccion_index" not in st.session_state:
    st.session_state.seccion_index = 0

# --- CORRECCIÓN DE VISIBILIDAD (CSS) ---
st.markdown("""
    <style>
    /* Corrige el color del texto en todos los inputs para que no sea blanco */
    input, div[data-baseweb="input"], textarea {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }
    /* Estilo para los títulos de los campos */
    label p {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    /* Estilo para los números en los inputs de tipo número */
    input[type=number] {
        color: #1a1a1a !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE APIS ---
def iniciar_servicios():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    secret_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_dict, scope)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds, static_discovery=False)
    return client, drive_service

def subir_a_drive(file, folder_id, drive_service):
    file_metadata = {'name': file.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    drive_service.permissions().create(fileId=uploaded_file.get('id'), body={'type': 'anyone', 'role': 'viewer'}).execute()
    return uploaded_file.get('webViewLink')

def obtener_o_crear_carpeta(nombre_carpeta, parent_id, drive_service):
    query = f"name='{nombre_carpeta}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    carpetas = response.get('files', [])
    if carpetas:
        return carpetas[0].get('id')
    file_metadata = {'name': nombre_carpeta, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    carpeta_nueva = drive_service.files().create(body=file_metadata, fields='id').execute()
    return carpeta_nueva.get('id')

# --- UI PRINCIPAL ---
render_hero("Cuadernillo Digital", f"Hola {usuario_activo.get('nombre', 'Conquistador')}, estás trabajando en tu clase de Amigo.", eyebrow="Club Lakonn")

# Definición de Secciones
secciones_lista = [
    "1. Datos Personales", 
    "2. Generales", 
    "3. Descubrimiento Espiritual", 
    "4. Sirviendo a los Demás"
]

# Sidebar con Radio sincronizado con el estado
seccion_actual = st.sidebar.radio(
    "Navegación:", 
    secciones_lista, 
    index=st.session_state.seccion_index,
    key="radio_nav"
)

# Actualizar el índice si el usuario cambia el radio manualmente
if secciones_lista.index(seccion_actual) != st.session_state.seccion_index:
    st.session_state.seccion_index = secciones_lista.index(seccion_actual)

# --- LÓGICA DE LAS SECCIONES ---

# SECCIÓN 1: DATOS PERSONALES
if seccion_actual == "1. Datos Personales":
    st.header("📋 I. DATOS PERSONALES")
    with st.form("form_personales"):
        col1, col2 = st.columns(2)
        with col1:
            n_f = st.text_input("Nombre completo", value=usuario_activo.get("nombre"))
            e_f = st.number_input("Edad", min_value=10, max_value=20, step=1)
            d_f = st.text_input("Dirección")
            b_f = st.text_input("Barrio")
        with col2:
            g_f = st.text_input("Grado / Año escolar")
            c_f = st.text_input("Ciudad / Provincia")
            t_f = st.text_input("Teléfono")
            em_f = st.text_input("Correo electrónico", value=usuario_activo.get("correo"))
        
        st.markdown("---")
        st.subheader("🏥 Información Médica")
        m1, m2, m3 = st.columns(3)
        ts = m1.selectbox("Tipo Sanguíneo", ["O", "A", "B", "AB", "No sé"])
        rh = m2.radio("Factor RH", ["+", "-"], horizontal=True)
        vt = m3.radio("Vacuna Antitetánica", ["Sí", "No"], horizontal=True)
        
        al = st.text_area("Alergias o condiciones médicas especiales")

        if st.form_submit_button("💾 GUARDAR DATOS PERSONALES", use_container_width=True):
            try:
                with st.spinner("Guardando en el libro RequisitosConquistadores..."):
                    client, _ = iniciar_servicios()
                    libro = client.open("RequisitosConquistadores")
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    hoja.append_row([
                        datetime.now().strftime("%d/%m/%Y"), usuario_activo.get("usuario"), 
                        "Datos Personales", f"Nombre: {n_f}, Edad: {e_f}, Tel: {t_f}, Sangre: {ts}{rh}, Alergias: {al}"
                    ])
                    st.success("¡Datos personales guardados!")
                    st.balloons()
            except Exception as e: st.error(f"Error: {e}")

    # Botón para avanzar a la siguiente sección
    if st.button("Siguiente sección: Generales ➡️", use_container_width=True):
        st.session_state.seccion_index = 1
        st.rerun()

# SECCIÓN 2: GENERALES
elif seccion_actual == "2. Generales":
    st.header("🎖️ II. GENERALES")
    
    st.markdown("### 1. Edad y Documentación")
    st.write("Tener como mínimo diez años de edad.")
    up_carnet = st.file_uploader("Sube tu Carnet o Certificado de Nacimiento", type=["jpg", "png", "pdf"])

    st.markdown("---")
    st.markdown("### 2. Miembro Activo")
    st.write("Sube fotos de tus mejores momentos en el Club este año.")
    up_fotos = st.file_uploader("Puedes subir varias fotos", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    st.markdown("---")
    st.markdown("### 3. Voto y Ley")
    txt_voto = st.text_area("Explica el significado del Voto con tus palabras:")
    txt_ley = st.text_area("Explica el significado de la Ley con tus palabras:")

    st.markdown("---")
    st.markdown("### 4, 5 y 6. Libros y Gema")
    inf_libro = st.text_area("Informe del Libro del Club de Lectura:")
    inf_camino = st.text_area("Resumen del libro 'El Camino a Cristo':")
    gema_listo = st.checkbox("He completado los requisitos de la Gema Bíblica")

    if st.button("🚀 GUARDAR CAPÍTULO: GENERALES", type="primary", use_container_width=True):
        try:
            with st.status("Subiendo a Drive y registrando...") as status:
                client, drive_service = iniciar_servicios()
                ID_PADRE = "1dmjbODLWcpimKiynkqFqeo-krXEco0ps"
                id_nino = obtener_o_crear_carpeta(usuario_activo.get("nombre"), ID_PADRE, drive_service)
                
                link_c = subir_a_drive(up_carnet, id_nino, drive_service) if up_carnet else "No subido"
                if up_fotos:
                    for f in up_fotos: subir_a_drive(f, id_nino, drive_service)
                
                libro = client.open("RequisitosConquistadores")
                hoja = libro.worksheet("Cuadernillo_Amigo")
                hoja.append_row([
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    usuario_activo.get("usuario"),
                    "Sección Generales",
                    f"Carnet: {link_c} | Gema: {gema_listo} | Voto/Ley: Completado"
                ])
                status.update(label="¡Sección Generales guardada exitosamente!", state="complete")
                st.balloons()
        except Exception as e: st.error(f"Error: {e}")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Anterior"):
            st.session_state.seccion_index = 0
            st.rerun()
    with col_btn2:
        if st.button("Siguiente: Espiritual ➡️"):
            st.session_state.seccion_index = 2
            st.rerun()

# SECCIÓN 3: DESCUBRIMIENTO ESPIRITUAL
elif seccion_actual == "3. Descubrimiento Espiritual":
    st.header("📖 III. DESCUBRIMIENTO ESPIRITUAL")
    st.info("Esta sección se habilitará pronto para completar los estudios bíblicos.")
    
    if st.button("⬅️ Volver a Generales"):
        st.session_state.seccion_index = 1
        st.rerun()

# --- BOTÓN PARA VOLVER AL MENÚ PRINCIPAL ---
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Volver al Menú Principal", use_container_width=True):
    st.switch_page("pages/menu.py")
