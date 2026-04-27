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
    # static_discovery=False es vital para evitar el error <Response [200]> en Streamlit Cloud
    drive_service = build('drive', 'v3', credentials=creds, static_discovery=False)
    return client, drive_service

def subir_a_drive(file, folder_id, drive_service):
    """Sube un archivo y lo hace público para ver con el link"""
    file_metadata = {'name': file.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    drive_service.permissions().create(fileId=uploaded_file.get('id'), body={'type': 'anyone', 'role': 'viewer'}).execute()
    return uploaded_file.get('webViewLink')

def obtener_o_crear_carpeta(nombre_carpeta, parent_id, drive_service):
    """Busca una carpeta por nombre. Si no existe, la crea."""
    query = f"name='{nombre_carpeta}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    carpetas = response.get('files', [])
    if carpetas:
        return carpetas[0].get('id')
    file_metadata = {'name': nombre_carpeta, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
    carpeta_nueva = drive_service.files().create(body=file_metadata, fields='id').execute()
    return carpeta_nueva.get('id')

# --- UI PRINCIPAL ---
render_hero("Cuadernillo Digital", f"Bienvenido {usuario_activo.get('nombre', 'Usuario')}. Completa tu cuadernillo de Amigo aquí.", eyebrow="Clase de Amigo")

# Menú lateral para navegar por secciones
secciones = [
    "1. Datos Personales", 
    "2. Generales", 
    "3. Descubrimiento Espiritual", 
    "Próximamente..."
]
seccion_actual = st.sidebar.radio("Navegación del Cuadernillo:", secciones)

# --- LÓGICA DE LAS SECCIONES ---

if seccion_actual == "1. Datos Personales":
    st.subheader("I. DATOS PERSONALES")
    with st.form("form_datos_completos"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_f = st.text_input("Nombre completo", value=usuario_activo.get("nombre"))
            edad_f = st.number_input("Edad", min_value=10, max_value=18, step=1)
            direccion_f = st.text_input("Dirección")
            barrio_f = st.text_input("Barrio")
            email_f = st.text_input("Correo electrónico", value=usuario_activo.get("correo"))
        with col2:
            grado_f = st.text_input("Grado / Año escolar")
            ciudad_f = st.text_input("Ciudad / Provincia")
            cp_f = st.text_input("Código Postal")
            telefono_f = st.text_input("Teléfono")

        st.markdown("---")
        st.write("**Información Médica**")
        m1, m2, m3 = st.columns(3)
        t_sangre = m1.selectbox("Tipo Sanguíneo", ["O", "A", "B", "AB", "No sé"])
        f_rh = m2.radio("Factor RH", ["+", "-"], horizontal=True)
        v_tetano = m3.radio("Vacuna Antitetánica", ["Sí", "No"], horizontal=True)
        
        st.write("**Condiciones (Marca si sufres de):**")
        en1, en2, en3, en4 = st.columns(4)
        diab = en1.checkbox("Diabetes")
        epil = en2.checkbox("Epilepsia")
        asma = en3.checkbox("Asma")
        card = en4.checkbox("Probl. Cardíacos")
        alergias = st.text_area("Otras alergias o condiciones (Penicilina, sueros, etc.)")

        if st.form_submit_button("💾 GUARDAR DATOS PERSONALES", use_container_width=True):
            try:
                with st.spinner("Conectando con RequisitosConquistadores..."):
                    client, _ = iniciar_servicios()
                    libro = client.open("RequisitosConquistadores")
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    
                    datos_fila = [
                        datetime.now().strftime("%d/%m/%Y"),
                        usuario_activo.get("usuario"),
                        nombre_f, edad_f, direccion_f, barrio_f, email_f, grado_f, ciudad_f, telefono_f,
                        f"{t_sangre}{f_rh}", v_tetano, str(diab), str(epil), str(asma), str(card), alergias
                    ]
                    hoja.append_row(datos_fila)
                    st.success("¡Datos guardados exitosamente!")
                    st.balloons()
            except Exception as e: st.error(f"Error al guardar: {e}")

elif seccion_actual == "2. Generales":
    st.subheader("I. GENERALES")
    
    # 1. Edad y Carnet
    st.markdown("#### 1. Tener como mínimo diez años de edad")
    archivo_carnet = st.file_uploader("Sube foto de tu Carnet o Certificado de Nacimiento", type=["jpg", "png", "jpeg", "pdf"], key="up_carnet")

    st.markdown("---")
    # 2. Miembro Activo
    st.markdown("#### 2. Ser miembro activo del Club de Conquistadores")
    fotos_actividades = st.file_uploader("Sube fotos de tus mejores momentos en el Club", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="up_fotos")

    st.markdown("---")
    # 3. Voto y Ley
    st.markdown("#### 3. Memorizar y explicar el Voto y la Ley")
    exp_voto = st.text_area("Explica el significado del VOTO con tus palabras:")
    exp_ley = st.text_area("Explica el significado de la LEY con tus palabras:")

    st.markdown("---")
    # 4 y 5. Lectura
    st.markdown("#### 4 y 5. Libros y Lectura")
    informe_club = st.text_area("Informe del Libro del Club de Lectura:")
    informe_camino = st.text_area("Resumen del libro 'El Camino a Cristo':")

    st.markdown("---")
    # 6. Gema Bíblica
    st.markdown("#### 6. Gema Bíblica")
    check_gema = st.checkbox("He completado todos los requisitos de la Gema Bíblica de Amigo")

    if st.button("🚀 GUARDAR TODA LA SECCIÓN GENERALES", type="primary", use_container_width=True):
        if not (exp_voto and exp_ley):
            st.warning("Por favor, completa las explicaciones del Voto y la Ley antes de guardar.")
        else:
            try:
                with st.status("Subiendo evidencias a Drive...") as status:
                    client, drive_service = iniciar_servicios()
                    ID_CARPETA_PADRE = "1dmjbODLWcpimKiynkqFqeo-krXEco0ps"
                    
                    # Carpeta individual del niño
                    id_nino = obtener_o_crear_carpeta(usuario_activo.get("nombre"), ID_CARPETA_PADRE, drive_service)
                    
                    # Subir carnet
                    link_c = subir_a_drive(archivo_carnet, id_nino, drive_service) if archivo_carnet else "No adjunto"
                    
                    # Subir fotos de actividades
                    if fotos_actividades:
                        for f in fotos_actividades: subir_a_drive(f, id_nino, drive_service)
                    
                    # Registro en Excel
                    libro = client.open("RequisitosConquistadores")
                    hoja = libro.worksheet("Cuadernillo_Amigo")
                    hoja.append_row([
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        usuario_activo.get("usuario"),
                        "SECCIÓN: GENERALES",
                        f"Carnet: {link_c} | Gema: {check_gema} | Voto: {exp_voto[:30]}... | Ley: {exp_ley[:30]}..."
                    ])
                    status.update(label="¡Capítulo I (Generales) guardado y sincronizado!", state="complete")
                    st.balloons()
            except Exception as e: st.error(f"Error: {e}")

else:
    st.info("🚧 Sección en desarrollo. Próximamente habilitaremos 'Descubrimiento Espiritual'.")

# Botón Volver
st.sidebar.markdown("---")
if st.sidebar.button("⬅️ Volver al Menú Principal", use_container_width=True):
    st.switch_page("pages/menu.py")
