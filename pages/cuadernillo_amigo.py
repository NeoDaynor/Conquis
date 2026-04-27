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

# --- CONFIGURACIÓN DE APIS (VERSIÓN ROBUSTA) ---
def iniciar_servicios():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    secret_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_dict, scope)
    
    client = gspread.authorize(creds)
    # static_discovery=False evita el error de red en Streamlit Cloud
    drive_service = build('drive', 'v3', credentials=creds, static_discovery=False)
    
    return client, drive_service

def subir_a_drive(file, folder_id, drive_service):
    """Sube un archivo y lo hace público para ver con el link"""
    file_metadata = {'name': file.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    # Permisos de lectura para cualquiera con el link
    drive_service.permissions().create(fileId=uploaded_file.get('id'), body={'type': 'anyone', 'role': 'viewer'}).execute()
    return uploaded_file.get('webViewLink')

def obtener_o_crear_carpeta(nombre_carpeta, parent_id, drive_service):
    """Busca una carpeta por nombre. Si no existe, la crea dentro del parent_id."""
    query = f"name='{nombre_carpeta}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    carpetas = response.get('files', [])

    if carpetas:
        return carpetas[0].get('id') # Ya existe, devuelve el ID
    else:
        # No existe, la crea
        file_metadata = {
            'name': nombre_carpeta,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        carpeta_nueva = drive_service.files().create(body=file_metadata, fields='id').execute()
        return carpeta_nueva.get('id')

# --- UI PRINCIPAL ---
render_hero(
    "Cuadernillo Digital",
    f"Bienvenido conqui {usuario_activo.get('nombre', 'Usuario')}. Completa tu cuadernillo de Amigo aquí.",
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
                    # CONEXIÓN EXACTA A TU LIBRO
                    libro = client.open("RequisitosConquistadores") 
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
                st.error(f"Error al conectar con Google Sheets: {e}")

elif seccion_actual == "2. Generales":
    st.subheader("II. GENERALES")
    st.write("1. Tener como mínimo diez años de edad.")
    st.info("Sube una foto o PDF de tu Certificado de Nacimiento o Carnet de Identidad.")
    
    archivo_id = st.file_uploader("Seleccionar archivo", type=["jpg", "png", "jpeg", "pdf"], key="uploader_generales")
    
    if st.button("🚀 SUBIR EVIDENCIA Y REGISTRAR", type="primary", use_container_width=True):
        if archivo_id:
            try:
                with st.status("Procesando evidencia en la nube...") as status:
                    client, drive_service = iniciar_servicios()
                    
                    # TU ID EXACTO DE LA CARPETA TarjetaAmigo
                    ID_CARPETA_PADRE = "1dmjbODLWcpimKiynkqFqeo-krXEco0ps"
                    
                    nombre_conquistador = usuario_activo.get("nombre", "Sin_Nombre")
                    
                    # Busca o crea la carpeta del niño dentro de TarjetaAmigo
                    status.update(label=f"Buscando o creando carpeta para {nombre_conquistador}...")
                    id_carpeta_nino = obtener_o_crear_carpeta(nombre_conquistador, ID_CARPETA_PADRE, drive_service)
                    
                    # Sube el archivo directamente a la carpeta del niño
                    status.update(label="Subiendo archivo...")
                    link_archivo = subir_a_drive(archivo_id, id_carpeta_nino, drive_service)
                    
                    # Guarda el registro en tu libro
                    status.update(label="Registrando en Excel...")
                    libro = client.open("RequisitosConquistadores")
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    
                    hoja.append_row([
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
                        usuario_activo.get("usuario"), 
                        "Evidencia: Carnet/Certificado", 
                        link_archivo
                    ])
                    
                    status.update(label=f"¡Éxito! Evidencia guardada.", state="complete")
                    st.success(f"Archivo subido correctamente a la carpeta de {nombre_conquistador}.")
                    st.markdown(f"🔗 [Abrir archivo subido]({link_archivo})")
                    st.balloons()
            except Exception as e:
                st.error(f"Error técnico en la subida: {e}")
        else:
            st.warning("⚠️ Debes seleccionar un archivo antes de presionar el botón.")

else:
    st.info("Esta sección se habilitará una vez completemos el mapeo del PDF.")

# Botón para volver
st.sidebar.markdown("---")
if st.sidebar.button("⬅️ Volver al Menú", use_container_width=True):
    st.switch_page("pages/menu.py")
