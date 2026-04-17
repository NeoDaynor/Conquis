import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE INFRAESTRUCTURA (GCP) ---
def get_gspread_client():
    # Se extraen las credenciales desde el panel de Secrets de Streamlit
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Inicialización de cliente y hoja
client = get_gspread_client()
sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Monitor Clase Amigo", layout="wide")

# --- LÓGICA DE ESTILO (HEATMAP) ---
def estilo_heatmap(val):
    """Pinta la celda de azul si contiene una fecha, ocultando el texto."""
    if val and str(val).strip() != "":
        # Azul sólido para celdas completadas
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# --- PROCESAMIENTO DE DATOS ---
data = sheet.get_all_values()
headers = data[1]  # Fila 2: Nombres de columnas reales
df_base = pd.DataFrame(data[2:], columns=headers)

# --- MAPEO DE DASHBOARD COMPACTO ---
mapeo_items = {
    "Item1": ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis"],
    "Item2": ["Éxodo", "Levítico", "Gemas Bíblicas"],
    "Item3": ["Salmo 23 o 46", "Personaje AT"],
    "Item4": ["2 Horas Ayuda Comunitaria", "Buen Ciudadano"],
    "Item5": ["Cuestionario Historia", "Daniel 1:8", "Temperancia de Daniel"],
    "Item6": ["Menú Vegetariano"],
    "Item7": ["Especialidad Natación I", "Especialidad Naturaleza", "Flores e Insectos"],
    "Item8": ["Nudos Básicos", "Nudos Avanzados", "Pernoctar Campamento", "Examen Seguridad"],
    "Item9": ["Armar Carpa"]
}

# Construcción de la vista acotada (Dashboard)
df_dash = df_base[['Integrantes', 'Ult. Actualizacion']].copy()

for item, preguntas in mapeo_items.items():
    for i, p_real in enumerate(preguntas):
        id_visual = f"{item}_P{i+1}"
        df_dash[id_visual] = df_base[p_real] if p_real in df_base.columns else ""

# --- INTERFAZ DE USUARIO ---
st.title("🛡️ Sistema de Gestión: Clase de Amigo")

st.subheader("📊 Cuadro de Cumplimiento")
# Se usa .map() en lugar de .applymap() para compatibilidad con Pandas 2.x
st.dataframe(
    df_dash.style.map(estilo_heatmap, subset=df_dash.columns[2:]),
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- SISTEMA DE ACTUALIZACIÓN ---
with st.expander("📝 Registrar Nuevos Avances"):
    conquistador = st.selectbox("Seleccione al Conquistador para actualizar:", df_base['Integrantes'].tolist())
    
    st.write("Marque los requisitos completados hoy:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Generales**")
        voto = st.checkbox("Saber de memoria el Voto")
        ley = st.checkbox("Saber de memoria la Ley")
        blanco = st.checkbox("Saber de memoria el Blanco")
        
    with col2:
        st.markdown("**Arte de Acampar**")
        nudos = st.checkbox("Nudos Básicos")
        carpa = st.checkbox("Saber armar Carpa")
        
    with col3:
        st.markdown("**Naturaleza**")
        natura = st.checkbox("Especialidad Naturaleza")

    if st.button("💾 ACTUALIZAR EN GOOGLE SHEETS"):
        # Localizar fila (Header en fila 2, datos inician en fila 3)
        fila_idx = df_base[df_base['Integrantes'] == conquistador].index[0] + 3
        hoy = datetime.now().strftime("%d/%m/%Y")
        
        # Diccionario de mapeo Checkbox -> Columna Real
        updates = {
            "Voto": voto, 
            "Ley": ley, 
            "Blanco": blanco,
            "Nudos Básicos": nudos,
            "Armar Carpa": carpa,
            "Especialidad Naturaleza": natura
        }
        
        # Actualización de celdas
        for req, marcado in updates.items():
            if marcado and req in headers:
                col_idx = headers.index(req) + 1
                sheet.update_cell(fila_idx, col_idx, hoy)
        
        # Actualizar columna de última fecha (Columna B)
        sheet.update_cell(fila_idx, 2, hoy)
        
        st.success(f"¡Progreso de {conquistador} sincronizado correctamente!")
        st.rerun()
