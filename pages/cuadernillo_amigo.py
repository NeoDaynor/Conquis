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

# --- NAVEGACIÓN FORZADA (STATE) ---
# Esta es la lista maestra de secciones. Debe coincidir exactamente.
secciones_lista = [
    "1. Datos Personales", 
    "2. Generales", 
    "3. Descubrimiento Espiritual", 
    "4. Sirviendo a los Demás"
]

if "nav_index" not in st.session_state:
    st.session_state.nav_index = 0

# --- CORRECCIÓN DE VISIBILIDAD Y COLORES (CSS) ---
st.markdown("""
    <style>
    /* Forzamos que el texto de CUALQUIER input sea negro sobre fondo blanco */
    input, textarea, [data-baseweb="select"] > div {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    /* Aseguramos que los números en inputs de edad sean negros */
    input[type="number"] {
        color: #000000 !important;
    }
    /* Labels en blanco para que resalten sobre el fondo oscuro de la app */
    label p {
        color: #ffffff !important;
        font-weight: bold;
        font-size: 1rem;
    }
    .stAlert p { color: #ffffff !important; }
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

# --- SIDEBAR (MENÚ LATERAL) ---
# Usamos el state para que el radio button cambie cuando presionamos botones
seccion_actual = st.sidebar.radio(
    "Navegación del Cuadernillo:", 
    secciones_lista, 
    index=st.session_state.nav_index,
    key="radio_navegacion"
)
# Sincronizamos el índice si el usuario hace clic manualmente en el radio
st.session_state.nav_index = secciones_lista.index(seccion_actual)

# --- CUERPO DE LA PÁGINA ---
render_hero("Cuadernillo Digital", f"Clase de Amigo: {usuario_activo.get('nombre')}", eyebrow="Club Lakonn")

# ==========================================
# SECCIÓN 1: DATOS PERSONALES (Página 2 PDF)
# ==========================================
if seccion_actual == "1. Datos Personales":
    st.header("📋 I. DATOS PERSONALES")
    with st.form("form_p1"):
        c1, c2 = st.columns(2)
        with c1:
            f_nom = st.text_input("Nombre", value=usuario_activo.get("nombre"))
            f_eda = st.number_input("Edad", min_value=10, max_value=20, step=1)
            f_gra = st.text_input("Grado / Año escolar")
            f_dir = st.text_input("Dirección")
            f_bar = st.text_input("Barrio")
            f_cp  = st.text_input("Código Postal")
            f_clu = st.text_input("Club", value="Lakonn")
            f_uni = st.text_input("Unidad")
        with c2:
            f_ciu = st.text_input("Ciudad")
            f_pro = st.text_input("Provincia")
            f_ema = st.text_input("Email", value=usuario_activo.get("correo"))
            f_tel = st.text_input("Teléfono")
            f_con = st.text_input("Consejero de Unidad")
            f_igl = st.text_input("Iglesia")
            f_aso = st.text_input("Asociación / Misión")
            f_union = st.text_input("Unión")

        st.markdown("---")
        st.subheader("🏥 INFORMACIÓN MÉDICA")
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
        
        f_ale = st.text_area("Alergias (Penicilina, suero, otros) o condiciones adicionales:")

        if st.form_submit_button("💾 GUARDAR DATOS PERSONALES", use_container_width=True):
            try:
                with st.spinner("Sincronizando con RequisitosConquistadores..."):
                    client, _ = iniciar_servicios()
                    libro = client.open("RequisitosConquistadores")
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    
                    fila = [
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        usuario_activo.get("usuario"),
                        f_nom, f_eda, f_dir, f_tel, f_ema, f_uni,
                        f"{f_sangre}{f_rh}", f_tetano, str(f_dia), str(f_asm), f_ale
                    ]
                    hoja.append_row(fila)
                    st.success("¡Datos guardados correctamente en tu libro!")
                    st.balloons()
            except Exception as e: st.error(f"Error: {e}")

    # BOTÓN DE NAVEGACIÓN FORZADA
    st.markdown("---")
    if st.button("IR A SECCIÓN 2: GENERALES ➡️", type="primary", use_container_width=True):
        st.session_state.nav_index = 1  # Forzamos índice a 1 (Sección 2)
        st.rerun()

# ==========================================
# SECCIÓN 2: GENERALES (Páginas 3-8 PDF)
# ==========================================
elif seccion_actual == "2. Generales":
    st.header("🎖️ II. REQUISITOS GENERALES")
    
    # 1. Edad
    st.markdown("#### 1. Edad y Documentación")
    st.write("Tener como mínimo diez años de edad.")
    up_carnet = st.file_uploader("Sube tu Carnet o Certificado de Nacimiento", type=["jpg", "png", "jpeg", "pdf"], key="up_c")

    st.markdown("---")
    # 2. Miembro Activo
    st.markdown("#### 2. Ser miembro activo del Club")
    up_fotos = st.file_uploader("Sube fotos de tus actividades", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="up_f")

    st.markdown("---")
    # 3. Voto y Ley
    st.markdown("#### 3. Memorizar y explicar el Voto y la Ley")
    txt_voto = st.text_area("¿Qué significa el VOTO para ti?", key="t_voto")
    txt_ley = st.text_area("¿Qué significa la LEY para ti?", key="t_ley")

    st.markdown("---")
    # 4 y 5. Lectura
    st.markdown("#### 4 y 5. Libros y Lectura")
    inf_club = st.text_area("Informe del Libro del Club de Lectura (Título y Resumen):", key="t_lib")
    inf_camino = st.text_area("Resumen del libro 'El Camino a Cristo':", key="t_cam")

    st.markdown("---")
    # 6. Gema Bíblica
    st.markdown("#### 6. Gema Bíblica")
    f_gema = st.checkbox("He completado los requisitos de la Gema Bíblica de Amigo", key="chk_gema")

    if st.button("🚀 GUARDAR CAPÍTULO I COMPLETO", type="primary", use_container_width=True):
        try:
            with st.status("Subiendo archivos a tu carpeta en Drive...") as status:
                client, drive_service = iniciar_servicios()
                ID_AMIGO = "1dmjbODLWcpimKiynkqFqeo-krXEco0ps"
                
                # Crear o buscar carpeta del niño
                id_nino = obtener_o_crear_carpeta(usuario_activo.get("nombre"), ID_AMIGO, drive_service)
                
                # Subir Carnet
                link_c = subir_a_drive(up_carnet, id_nino, drive_service) if up_carnet else "No subido"
                # Subir fotos de actividades
                if up_fotos:
                    for f in up_fotos: subir_a_drive(f, id_nino, drive_service)
                
                # Registrar en Excel
                libro = client.open("RequisitosConquistadores")
                hoja = libro.worksheet("Cuadernillo_Amigo")
                hoja.append_row([
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    usuario_activo.get("usuario"),
                    "REQUISITOS GENERALES",
                    f"Carnet: {link_c} | Gema: {f_gema} | Voto/Ley: Explicados"
                ])
                status.update(label="¡Capítulo I guardado en Drive y Excel!", state="complete")
                st.balloons()
        except Exception as e: st.error(f"Error técnico: {e}")

    # BOTONES DE NAVEGACIÓN
    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("⬅️ Volver a Datos Personales"):
            st.session_state.nav_index = 0
            st.rerun()
    with b2:
        if st.button("Ir a Sección 3: Espiritual ➡️"):
            st.session_state.nav_index = 2
            st.rerun()

# ==========================================
# SECCIÓN 3: DESCUBRIMIENTO ESPIRITUAL
# ==========================================
elif seccion_actual == "3. Descubrimiento Espiritual":
    st.header("📖 III. DESCUBRIMIENTO ESPIRITUAL")
    st.info("Esta sección se está preparando basándose en el PDF de estudios bíblicos.")
    if st.button("⬅️ Anterior"):
        st.session_state.nav_index = 1
        st.rerun()

# --- VOLVER AL MENÚ ---
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Volver al Panel Principal", use_container_width=True):
    st.switch_page("pages/menu.py")
