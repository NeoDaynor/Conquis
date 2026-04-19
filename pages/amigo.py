import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz
import base64

# --- CONFIGURACIÓN Y SEGURIDAD (RESTAURADA) ---
st.set_page_config(page_title="Gestión Club Lakonn", layout="wide", initial_sidebar_state="collapsed")
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

usuario_activo = st.session_state.get("user_info")
unidad_actual = st.session_state.get("unidad_seleccionada")

# --- CONEXIÓN ---
@st.cache_resource
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

client = get_client()
spreadsheet = client.open("RequisitosConquistadores")
sheet = spreadsheet.worksheet("Amigo")
log_sheet = spreadsheet.worksheet("Log_Cambios")

# --- LECTURA DE DATOS (CRÍTICO) ---
# Leemos TODA la hoja para tener la referencia de filas real de Google Sheets
raw_data = sheet.get_all_values()
# Tus encabezados reales están en la FILA 2 de Excel (índice 1 de la lista)
headers = [h.strip() for h in raw_data[1]] 
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- ESTILOS (RESTAURADOS) ---
def get_base64(file):
    try: return base64.b64encode(open(file, 'rb').read()).decode()
    except: return ""

img_pc = get_base64('images/fondopc.jpg')
img_mob = get_base64('images/fondocelu.webp')

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("data:image/jpg;base64,{img_pc}"); background-size: cover; }}
    [data-testid="stVerticalBlock"] > div:has(div[data-testid="stVerticalBlock"]) {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px; border-radius: 12px; border: 1px solid #0070C0;
    }}
    </style>
""", unsafe_allow_html=True)

# --- INTERFAZ ---
st.markdown(f"## UNIDAD: {unidad_actual}")

nombres = df_unidad['Integrantes'].tolist()
if nombres:
    conquistador = st.selectbox("Seleccione Integrante:", nombres)
    fila_persona_df = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]

    # Categorías (Asegúrate que estos nombres sean EXACTOS a los de la Fila 2 de tu Excel)
    items_a_marcar = [
        "Voto y Ley", "Libro año en curso", "Libro Por la gracia de Dios", "Clase Biblica",
        "Explicar la Creacion", "Explicar 10 Plaga", "Nombre 12 Tribus", "39 Libros A.T.",
        "Explicar Juan 3:16", "Explicar II Timoteo 3:16", "Explicar Efesios 6:1-3", 
        "Explicar Salmo 1", "Lectura Biblica", "Visitar a alguien", "Dar alimento", "Buen Ciudadano"
    ]

    nuevo_estado = {}
    cols = st.columns(3)
    for i, item in enumerate(items_a_marcar):
        with cols[i % 3]:
            valor_actual = bool(fila_persona_df.get(item) and str(fila_persona_df.get(item)).strip() != "")
            nuevo_estado[item] = st.checkbox(item, value=valor_actual, key=f"check_{conquistador}_{item}")

    if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
        try:
            # --- LÓGICA DE PRECISIÓN ---
            # 1. Buscar la fila real (Nombre en Columna B / Índice 1)
            # Recorremos la columna B de los datos crudos para no fallar
            nombres_col_b = [r[1] for r in raw_data] 
            fila_excel_real = nombres_col_b.index(conquistador) + 1 # +1 porque gspread empieza en 1
            
            updates = []
            logs = []
            hoy = ahora_chile.strftime("%d/%m/%Y")
            
            for req, marcado in nuevo_estado.items():
                estaba_marcado = bool(fila_persona_df.get(req) and str(fila_persona_df.get(req)).strip() != "")
                
                if req in headers:
                    col_excel_real = headers.index(req) + 1
                    
                    if marcado and not estaba_marcado:
                        updates.append({'range': gspread.utils.rowcol_to_a1(fila_excel_real, col_excel_real), 'values': [[hoy]]})
                        logs.append([ahora_chile.strftime("%d/%m/%Y %H:%M:%S"), usuario_activo['nombre'], conquistador, req, "Marcado"])
                    elif not marcado and estaba_marcado:
                        updates.append({'range': gspread.utils.rowcol_to_a1(fila_excel_real, col_excel_real), 'values': [[""]]})
                        logs.append([ahora_chile.strftime("%d/%m/%Y %H:%M:%S"), usuario_activo['nombre'], conquistador, req, "Desmarcado"])

            if updates:
                # Actualizar también la columna de última actualización si existe
                if "Ult. Actualizacion" in headers:
                    col_upd = headers.index("Ult. Actualizacion") + 1
                    updates.append({'range': gspread.utils.rowcol_to_a1(fila_excel_real, col_upd), 'values': [[hoy]]})
                
                # EJECUCIÓN
                sheet.batch_update(updates)
                log_sheet.append_rows(logs)
                st.success(f"¡Sincronizado! Fila {fila_excel_real} actualizada.")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.info("No hay cambios para guardar.")

        except Exception as e:
            st.error(f"Error de red: {e}")
