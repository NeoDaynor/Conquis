import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURACIÓN ---
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

@st.cache_resource
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

client = get_client()
spreadsheet = client.open("RequisitosConquistadores")
sheet = spreadsheet.worksheet("Amigo")
log_sheet = spreadsheet.worksheet("Log_Cambios")

# LEER DATOS: Forzamos la lectura desde la fila 2 que es donde están tus encabezados reales
# según se ve en tu imagen de la hoja de cálculo.
raw_values = sheet.get_all_values()
headers = raw_values[1] # Fila 2 de Excel
df_full = pd.DataFrame(raw_values[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == st.session_state.get("unidad_seleccionada")].copy()

# --- INTERFAZ ---
st.title(f"Unidad: {st.session_state.get('unidad_seleccionada')}")

nombres = df_unidad['Integrantes'].tolist()
if nombres:
    conquistador = st.selectbox("Seleccione Integrante:", nombres)
    # Obtenemos los datos actuales de la persona
    datos_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]

    # Categorías según tu nueva estructura de 9 columnas
    categorias = {
        "GENERALES": ["Voto y Ley", "Libro año en curso", "Libro Por la gracia de Dios", "Clase Biblica"],
        "DESCUBRIMIENTO": ["Explicar la Creacion", "Explicar 10 Plaga", "Nombre 12 Tribus", "39 Libros A.T."],
        "SIRVIENDO": ["Visitar a alguien", "Dar alimento", "Buen Ciudadano"]
    }

    nuevo_estado = {}
    cols = st.columns(3)
    
    for i, (cat, items) in enumerate(categorias.items()):
        with cols[i]:
            st.markdown(f"**{cat}**")
            for item in items:
                # Marcamos si ya tiene una fecha escrita en la celda
                valor_actual = str(datos_persona.get(item, "")).strip()
                nuevo_estado[item] = st.checkbox(item, value=(valor_actual != ""), key=f"cb_{conquistador}_{item}")

    if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
        try:
            # 1. LOCALIZAR FILA: Buscamos el nombre en la columna 'Integrantes' (Columna B)
            # Sumamos 1 por el índice de lista y +2 por las filas de encabezado = +3
            nombres_en_sheet = [r[headers.index('Integrantes')] for r in raw_values[2:]]
            fila_excel = nombres_en_sheet.index(conquistador) + 3 
            
            hoy = ahora_chile.strftime("%d/%m/%Y")
            logs = []
            
            with st.status("Actualizando Google Sheets...") as s:
                for req, marcado in nuevo_estado.items():
                    # Valor que tiene actualmente el DataFrame
                    estaba_marcado = str(datos_persona.get(req, "")).strip() != ""
                    
                    if req in headers:
                        col_idx = headers.index(req) + 1 # gspread usa base 1
                        
                        # Si el usuario lo marcó y no estaba: Ponemos fecha
                        if marcado and not estaba_marcado:
                            sheet.update_cell(fila_excel, col_idx, hoy)
                            logs.append([ahora_chile.strftime("%d/%m/%Y %H:%M:%S"), st.session_state.user_info['nombre'], conquistador, req, "Marcado"])
                        
                        # Si el usuario lo desmarcó y estaba: Borramos celda
                        elif not marcado and estaba_marcado:
                            sheet.update_cell(fila_excel, col_idx, "")
                            logs.append([ahora_chile.strftime("%d/%m/%Y %H:%M:%S"), st.session_state.user_info['nombre'], conquistador, req, "Desmarcado"])

                # ACTUALIZAR COLUMNA "Ult. Actualizacion"
                if "Ult. Actualizacion" in headers:
                    col_u = headers.index("Ult. Actualizacion") + 1
                    sheet.update_cell(fila_excel, col_u, hoy)

                if logs:
                    log_sheet.append_rows(logs)
                
                s.update(label="¡Guardado correctamente!", state="complete")
            
            st.success(f"Se actualizaron los requisitos de {conquistador}")
            st.cache_resource.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Error al guardar: {e}")
