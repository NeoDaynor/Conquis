import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD (STREAMLIT SECRETS) ---
def get_gspread_client():
    # En la nube, leeremos las credenciales desde st.secrets
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

client = get_gspread_client()
sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- INTERFAZ ---
st.set_page_config(page_title="Monitor Amigo", layout="wide")

# Lógica del Dashboard Compacto (Heatmap)
def estilo_azul(val):
    if val and str(val).strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# Carga de datos
data = sheet.get_all_values()
headers = data[1] # Fila 2
df_base = pd.DataFrame(data[2:], columns=headers)

# Mapeo de Items (Dashboard)
mapeo = {
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

# Construir Dashboard
df_dash = df_base[['Integrantes', 'Ult. Actualizacion']].copy()
for item, preguntas in mapeo.items():
    for i, p_real in enumerate(preguntas):
        col_name = f"{item}_P{i+1}"
        df_dash[col_name] = df_base[p_real] if p_real in df_base.columns else ""

st.title("🛡️ Sistema de Gestión: Clase de Amigo")
st.dataframe(df_dash.style.applymap(estilo_azul, subset=df_dash.columns[2:]), use_container_width=True, hide_index=True)

# (Aquí iría el resto del formulario de actualización que ya tenemos)