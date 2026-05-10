# utils.py
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

def registrar_actividad(accion, pagina_actual):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Usa los secretos que configuramos en el paso 2
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        cliente = gspread.authorize(creds)

        # Abre la hoja y la pestaña
        documento = cliente.open("RequisitosConquistadores")
        hoja_log = documento.worksheet("Log_Acceso")

        # Configura la hora (ejemplo: Chile/Santiago)
        tz = pytz.timezone('America/Santiago')
        fecha_hora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

        # Obtiene el usuario si existe en la sesión
        usuario = st.session_state.get("usuario", "No identificado")

        # Prepara y envía la fila
        fila = [fecha_hora, usuario, pagina_actual, accion]
        hoja_log.append_row(fila)
    except Exception as e:
        st.error(f"Error al registrar log: {e}")
