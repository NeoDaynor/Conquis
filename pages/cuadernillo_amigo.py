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
render_hero("Cuadernillo Digital", f"Hola {usuario_activo.get('nombre')}, completa tu clase de Amigo.", eyebrow="Clase de Amigo")

secciones = ["1. Datos Personales", "2. Generales", "3. Descubrimiento Espiritual", "Próximamente..."]
seccion_actual = st.sidebar.radio("Navegación:", secciones)

# --- LÓGICA DE SECCIONES ---

if seccion_actual == "1. Datos Personales":
    st.subheader("I. DATOS PERSONALES")
    with st.form("form_datos"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre completo", value=usuario_activo.get("nombre"))
            edad = st.number_input("Edad", min_value=10, max_value=16)
            direccion = st.text_input("Dirección")
        with c2:
            grado = st.text_input("Grado escolar")
            ciudad = st.text_input("Ciudad")
            telefono = st.text_input("Teléfono")
        
        if st.form_submit_button("💾 GUARDAR DATOS PERSONALES", use_container_width=True):
            try:
                client, _ = iniciar_servicios()
                libro = client.open("RequisitosConquistadores")
                hoja = libro.worksheet("Cuadernillo_Amigo")
                hoja.append_row([datetime.now().strftime("%d/%m/%Y"), usuario_activo.get("usuario"), "Datos Personales", f"Edad: {edad}, Dir: {direccion}, Tel: {telefono}"])
                st.success("¡Datos guardados!")
            except Exception as e: st.error(f"Error: {e}")

elif seccion_actual == "2. Generales":
    st.subheader("I. GENERALES")
    
    # 1. Edad y Carnet
    st.markdown("### 1. Edad y Documentación")
    st.write("Tener como mínimo diez años de edad.")
    archivo_id = st.file_uploader("Sube tu Carnet o Certificado", type=["jpg", "png", "pdf"], key="up_1")
    
    st.markdown("---")
    # 2. Miembro Activo
    st.markdown("### 2. Miembro Activo")
    st.write("Pega fotos de los momentos más importantes del año.")
    fotos_actividad = st.file_uploader("Subir fotos de actividades", type=["jpg", "png"], accept_multiple_files=True, key="up_2")
    
    st.markdown("---")
    # 3. Voto y Ley
    st.markdown("### 3. Voto y Ley")
    explicacion_voto = st.text_area("Explica con tus palabras el significado del Voto del Conquistador:")
    explicacion_ley = st.text_area("Explica con tus palabras el significado de la Ley del Conquistador:")

    st.markdown("---")
    # 4 y 5. Lectura
    st.markdown("### 4 y 5. Libros y Lectura")
    resumen_club = st.text_area("Escribe un breve resumen del libro del Club de Lectura de este año:")
    resumen_camino = st.text_area("Escribe un breve resumen del libro 'El Camino a Cristo':")

    st.markdown("---")
    # 6. Gema Bíblica
    st.markdown("### 6. Gema Bíblica")
    gema_completa = st.checkbox("He completado los requisitos de la Gema Bíblica")

    if st.button("🚀 GUARDAR TODA LA SECCIÓN GENERALES", type="primary", use_container_width=True):
        try:
            with st.status("Sincronizando sección Generales...") as status:
                client, drive_service = iniciar_servicios()
                ID_CARPETA_PADRE = "1dmjbODLWcpimKiynkqFqeo-krXEco0ps"
                id_nino = obtener_o_crear_carpeta(usuario_activo.get("nombre"), ID_CARPETA_PADRE, drive_service)
                
                # Subir Carnet
                link_carnet = subir_a_drive(archivo_id, id_nino, drive_service) if archivo_id else "No subido"
                
                # Subir Fotos (solo la primera como ejemplo para el Sheets)
                link_fotos = "Varios archivos en Drive" if fotos_actividad else "Sin fotos"
                if fotos_actividad:
                    for foto in fotos_actividad:
                        subir_a_drive(foto, id_nino, drive_service)
                
                # Guardar en Sheets
                libro = client.open("RequisitosConquistadores")
                hoja = libro.worksheet("Cuadernillo_Amigo")
                hoja.append_row([
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    usuario_activo.get("usuario"),
                    "Capítulo: Generales",
                    f"Carnet: {link_carnet} | Voto: {explicacion_voto[:50]}... | Ley: {explicacion_ley[:50]}... | Resumenes listos | Gema: {gema_completa}"
                ])
                status.update(label="¡Todo guardado en tu carpeta de Drive y en el Excel!", state="complete")
                st.balloons()
        except Exception as e: st.error(f"Error: {e}")

else:
    st.info("Esta sección se activará pronto.")

# Botón Volver
st.sidebar.markdown("---")
if st.sidebar.button("⬅️ Volver al Menú", use_container_width=True):
    st.switch_page("pages/menu.py")
