import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

# --- SEGURIDAD Y ZONA HORARIA ---
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

unidad_actual = st.session_state.get("unidad_seleccionada")
usuario_activo = st.session_state.get("user_info")

# --- FUNCIONES DE IMAGEN ---
def get_base64(file):
    try:
        with open(file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

# --- CSS INTEGRAL (RESTAURADO) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}
    @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    .main-card {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #0070C0;
        margin-bottom: 20px;
        color: #1E293B;
    }}
    .header-box {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #0070C0;
        margin-bottom: 20px;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: #0070C0 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 50px;
    }}
    /* Estilo para la tabla del Dashboard */
    .stDataFrame {{ background-color: white; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
@st.cache_resource
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

client = get_client()
spreadsheet = client.open("RequisitosConquistadores")
sheet = spreadsheet.worksheet("Amigo")
log_sheet = spreadsheet.worksheet("Log_Cambios")

# Lectura de datos crudos para posiciones exactas
raw_values = sheet.get_all_values()
headers = [h.strip() for h in raw_values[1]] # Fila 2
df_full = pd.DataFrame(raw_values[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---
st.markdown(f'<div class="header-box"><h2 style="color:#0070C0; margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER AL MENU"):
    st.switch_page("pages/menu.py")

# --- BLOQUE 1: DASHBOARD DE AVANCE GENERAL (RESTAURADO) ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Dashboard de Avance: General")
    # Mostramos las columnas principales para el dashboard
    cols_visualizar = ["Integrantes", "Ult. Actualizacion", "Voto y Ley", "Clase Biblica", "Lectura Biblica"]
    cols_existentes = [c for c in cols_visualizar if c in df_unidad.columns]
    st.dataframe(df_unidad[cols_existentes], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- BLOQUE 2: REGISTRO DE AVANCES ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Registro de Avances (Solo Líderes/Admin)")
    
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione Integrante:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        # Categorías organizadas
        categorias = {
            "GENERALES": ["Voto y Ley", "Libro año en curso", "Libro Por la gracia de Dios", "Clase Biblica"],
            "DESCUBRIMIENTO": ["Explicar la Creacion", "Explicar 10 Plaga", "Nombre 12 Tribus", "39 Libros A.T.", "Explicar Juan 3:16", "Explicar II Timoteo 3:16", "Explicar Efesios 6:1-3", "Explicar Salmo 1", "Lectura Biblica"],
            "SIRVIENDO": ["Visitar a alguien", "Dar alimento", "Proyecto ecológico/educativo", "Buen Ciudadano"]
        }

        cols = st.columns(3)
        nuevo_estado = {}

        for i, (cat_nombre, items) in enumerate(categorias.items()):
            with cols[i]:
                st.markdown(f"**{cat_nombre}**")
                for item in items:
                    if item in headers:
                        valor_actual = bool(fila_persona.get(item) and str(fila_persona.get(item)).strip() != "")
                        nuevo_estado[item] = st.checkbox(item, value=valor_actual, key=f"check_{conquistador}_{item}")

        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
            try:
                # Localización en el Excel real
                nombres_col = [r[headers.index('Integrantes')] for r in raw_values]
                fila_excel = nombres_col.index(conquistador) + 1
                
                hoy = ahora_chile.strftime("%d/%m/%Y")
                updates = []
                logs = []
                
                for req, marcado in nuevo_estado.items():
                    estaba_marcado = bool(fila_persona.get(req) and str(fila_persona.get(req)).strip() != "")
                    col_idx = headers.index(req) + 1
                    
                    if marcado and not estaba_marcado:
                        updates.append({'range': gspread.utils.rowcol_to_a1(fila_excel, col_idx), 'values': [[hoy]]})
                        logs.append([ahora_chile.strftime("%d/%m/%Y %H:%M:%S"), usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                    elif not marcado and estaba_marcado:
                        updates.append({'range': gspread.utils.rowcol_to_a1(fila_excel, col_idx), 'values': [[""]]})
                        logs.append([ahora_chile.strftime("%d/%m/%Y %H:%M:%S"), usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])

                if updates:
                    if "Ult. Actualizacion" in headers:
                        col_u = headers.index("Ult. Actualizacion") + 1
                        updates.append({'range': gspread.utils.rowcol_to_a1(fila_excel, col_u), 'values': [[hoy]]})
                    
                    sheet.batch_update(updates)
                    if logs: log_sheet.append_rows(logs)
                    st.success("Sincronización exitosa.")
                    st.cache_resource.clear()
                    st.rerun()
                else:
                    st.info("No se detectaron cambios.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
