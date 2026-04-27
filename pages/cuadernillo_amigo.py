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

# --- CONFIGURACIÓN DE APIS ---
def iniciar_servicios():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # Usamos tus secretos ya configurados en Streamlit
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return client, drive_service

def subir_a_drive(file, folder_id, drive_service):
    """Sube un archivo y lo hace público para ver con el link"""
    file_metadata = {'name': file.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    # Permisos de lectura para cualquiera con el link
    drive_service.permissions().create(fileId=uploaded_file.get('id'), body={'type': 'anyone', 'role': 'viewer'}).execute()
    return uploaded_file.get('webViewLink')

# --- UI PRINCIPAL ---
render_hero(
    "Cuadernillo Digital",
    f"Bienvenido conqui {usuario_activo.get('nombre')}. Completa tu cuadernillo de Amigo aquí.",
    eyebrow="Clase de Amigo"
)

# Menú lateral para navegar por secciones
secciones = [
    "1. Datos Personales",
    "2. Generales",
    "3. Descubrimiento Espiritual",
    "En construcción..."
]
seccion_actual = st.sidebar.radio("Ir a sección:", secciones)

# --- LÓGICA DE SECCIONES ---

if seccion_actual == "1. Datos Personales":
    st.subheader("I. DATOS PERSONALES")
    
    with st.form("form_datos"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre completo", value=usuario_activo.get("nombre"))
            edad = st.number_input("Edad", min_value=10, max_value=16)
            direccion = st.text_input("Dirección")
            email = st.text_input("Correo", value=usuario_activo.get("correo"))
        with c2:
            grado = st.text_input("Grado escolar")
            ciudad = st.text_input("Ciudad")
            telefono = st.text_input("Teléfono")
        
        st.markdown("---")
        st.write("**Información Médica**")
        col_m1, col_m2 = st.columns(2)
        tipo_sangre = col_m1.selectbox("Tipo de sangre", ["A", "B", "AB", "O", "No sé"])
        rh = col_m2.radio("Factor RH", ["+", "-"], horizontal=True)
        
        otros = st.text_area("Alergias o condiciones médicas")
        
        # BOTÓN DE GUARDADO
        if st.form_submit_button("💾 GUARDAR DATOS PERSONALES", use_container_width=True):
            try:
                with st.spinner("Guardando en la nube..."):
                    client, _ = iniciar_servicios()
                    # ⚠️ CAMBIA ESTO POR EL NOMBRE DE TU EXCEL
                    libro = client.open("GESTION CLUB LAKONN") 
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    
                    nueva_fila = [
                        datetime.now().strftime("%d/%m/%Y"),
                        usuario_activo.get("usuario"),
                        nombre, edad, direccion, email, grado, ciudad, telefono,
                        f"{tipo_sangre} {rh}", otros
                    ]
                    hoja.append_row(nueva_fila)
                    st.success("¡Datos personales guardados correctamente!")
                    st.balloons()
            except Exception as e:
                st.error(f"Error al conectar con Google: {e}")

elif seccion_actual == "2. Generales":
    st.subheader("II. GENERALES")
    st.write("1. Tener como mínimo diez años de edad.")
    
    archivo_id = st.file_uploader("Sube tu Certificado de Nacimiento o Carnet (Imagen o PDF)", type=["jpg", "png", "pdf"])
    
    if st.button("🚀 SUBIR EVIDENCIA", type="primary"):
        if archivo_id:
            try:
                with st.spinner("Subiendo archivo a Drive..."):
                    client, drive_service = iniciar_servicios()
                    
                    # ⚠️ CAMBIA ESTO POR EL ID DE TU CARPETA "AMIGO" EN DRIVE
                    ID_CARPETA_DRIVE = "TU_ID_AQUI" 
                    
                    link_archivo = subir_a_drive(archivo_id, ID_CARPETA_DRIVE, drive_service)
                    
                    # Guardamos el link en el Sheet
                    libro = client.open("GESTION CLUB LAKONN")
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    # Buscamos la fila del usuario para actualizar o agregamos nueva
                    hoja.append_row([datetime.now().strftime("%d/%m/%Y"), usuario_activo.get("usuario"), "SUBIDA_ARCHIVO", link_archivo])
                    
                    st.success(f"¡Archivo subido! Puedes verlo aquí: {link_archivo}")
            except Exception as e:
                st.error(f"Error al subir: {e}")
        else:
            st.warning("Por favor selecciona un archivo primero.")

else:
    st.info("Esta sección se habilitará una vez completemos el mapeo del PDF.")

# Botón para volver
if st.sidebar.button("⬅️ Volver al Menú"):
    st.switch_page("pages/menu.py")
