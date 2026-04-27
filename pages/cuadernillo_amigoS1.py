import streamlit as st
import io
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from ui_theme import apply_app_theme, render_hero

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sección 1: Generales", layout="wide")

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

usuario_activo = st.session_state.get("user_info", {})
apply_app_theme(max_width=1100)

# CSS para visibilidad
st.markdown("""
    <style>
    input, textarea, [data-baseweb="input"] { color: #000000 !important; background-color: #ffffff !important; }
    label p { color: #ffffff !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A APIS ---
def iniciar_servicios():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    return gspread.authorize(creds), build('drive', 'v3', credentials=creds, static_discovery=False)

def subir_a_drive(file, folder_id, drive_service):
    file_metadata = {'name': file.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type, resumable=True)
    up = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    drive_service.permissions().create(fileId=up.get('id'), body={'type': 'anyone', 'role': 'viewer'}).execute()
    return up.get('webViewLink')

def obtener_o_crear_carpeta(nombre, parent_id, drive_service):
    query = f"name='{nombre}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    res = drive_service.files().list(q=query, spaces='drive', fields='files(id)').execute().get('files', [])
    if res: return res[0]['id']
    meta = {'name': nombre, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    return drive_service.files().create(body=meta, fields='id').execute()['id']

# --- UI PRINCIPAL ---
render_hero("Sección 1: Generales", "Requisitos Generales - Clase de Amigo", eyebrow="Cuadernillo Digital")

st.markdown("#### 1. Tener como mínimo diez años de edad")
up_carnet = st.file_uploader("Sube tu Carnet o Certificado de Nacimiento (JPG, PNG, PDF)", type=["jpg", "png", "pdf"])

st.markdown("---")
st.markdown("#### 2. Ser miembro activo del Club de Conquistadores")
txt_activo = st.text_area("Da un resumen de las actividades que realizas en el Club:")
up_fotos = st.file_uploader("Sube fotos de tus actividades en el Club", type=["jpg", "png"], accept_multiple_files=True)

st.markdown("---")
st.markdown("#### 3. Memorizar y explicar el Voto y la Ley")
txt_voto = st.text_area("Explica con tus palabras el significado del Voto:")
txt_ver_voto = st.text_area("Busca un versículo biblico que corrobore el significado del Voto:")
txt_ley = st.text_area("Explica con tus palabras el significado de la Ley:")
txt_ver_ley = st.text_area("Busca un versículo biblico que confirme el significado de la Ley:")

st.markdown("---")
st.markdown("#### 4 y 5. Club de Lectura y El Camino a Cristo")
txt_club = st.text_area("Informe del Libro del Club de Lectura (Escribe un resumen detallado):")
txt_camino = st.text_area("Resumen del libro 'El Camino a Cristo':")

st.markdown("---")
st.markdown("#### 6. Gema Bíblica")
chk_gema = st.checkbox("Declaro que he completado todos los requisitos de la Gema Bíblica de Amigo")

if st.button("🚀 GUARDAR SECCIÓN GENERALES", type="primary", use_container_width=True):
    try:
        with st.status("Subiendo evidencias y guardando datos...") as status:
            client, drive = iniciar_servicios()
            # Carpeta TarjetaAmigo
            id_nino = obtener_o_crear_carpeta(usuario_activo.get("nombre"), "1dmjbODLWcpimKiynkqFqeo-krXEco0ps", drive)
            
            status.update(label="Subiendo archivos a Drive...")
            link_c = subir_a_drive(up_carnet, id_nino, drive) if up_carnet else "No subido"
            
            links_f = []
            if up_fotos:
                for f in up_fotos:
                    links_f.append(subir_a_drive(f, id_nino, drive))
            texto_links_fotos = " | ".join(links_f) if links_f else "No subidas"
            
            status.update(label="Registrando en Excel...")
            hoja = client.open("RequisitosConquistadores").worksheet("C_Amigo_Generales")
            
            fila = [
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                usuario_activo.get("usuario"),
                link_c, texto_links_fotos, txt_voto, txt_ley, txt_club, txt_camino, str(chk_gema)
            ]
            hoja.append_row(fila)
            status.update(label="¡Sección Generales completada con éxito!", state="complete")
            st.balloons()
    except Exception as e:
        st.error(f"Error al guardar: {e}")

# --- NAVEGACIÓN ---
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    if st.button("⬅️ Volver a Datos Personales", use_container_width=True):
        st.switch_page("pages/cuadernillo_amigo.py")
with c2:
    if st.button("Siguiente: Descubrimiento Espiritual ➡️", use_container_width=True):
        st.switch_page("pages/cuadernillo_amigoS2.py")

st.sidebar.markdown("---")
if st.sidebar.button("🏠 Menú Principal", use_container_width=True):
    st.switch_page("pages/menu.py")
