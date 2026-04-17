import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

# --- SEGURIDAD Y ZONA HORARIA ---
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

unidad_actual = st.session_state.get("unidad_seleccionada")
usuario_activo = st.session_state.get("user_info")

# --- ESTILOS CSS REFORZADOS (CORRECCIÓN DE ENVOLTORIO) ---
def aplicar_estilos_v4():
    st.markdown(
        """
        <style>
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        
        :root {
            --bg-page: #F8FAFC;
            --bg-card: #FFFFFF;
            --border: #E2E8F0;
            --text: #1E293B;
            --accent: #0070C0;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg-page: #0E1117;
                --bg-card: #1E293B;
                --border: #334155;
                --text: #F1F5F9;
                --accent: #3B82F6;
            }
        }

        .stApp { background-color: var(--bg-page); color: var(--text); }

        /* TARJETA PERSONALIZADA: Ahora con forzado de envoltorio */
        .custom-card {
            background-color: var(--bg-card);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            margin-bottom: 25px;
            width: 100%;
            display: block;
            overflow: auto; /* CRÍTICO: Esto obliga al DIV a envolver todo el contenido interno */
        }

        .unidad-header {
            text-align: center;
            padding: 15px;
            background-color: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
        }

        .inline-warning {
            color: #F59E0B;
            font-size: 0.8rem;
            font-weight: bold;
            display: block;
            margin-top: -10px;
        }

        div.stButton > button[kind="primary"] {
            background-color: var(--accent) !important;
            color: white !important;
            height: 55px;
            font-weight: bold;
            width: 100%;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_v4()

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

raw_data = sheet.get_all_values()
headers = raw_data[1]
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---

st.markdown(f'<div class="unidad-header"><h2 style="color:var(--accent); margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER AL PANEL"):
    st.switch_page("app.py")

# BLOQUE 1: AVANCE GENERAL
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown("### 📊 Avance General de Unidad")
st.dataframe(
    df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.2); color: var(--accent); font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
    use_container_width=True, hide_index=True
)
st.markdown('</div>', unsafe_allow_html=True)

# BLOQUE 2: REGISTRO DE AVANCES
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown("### 📝 Registro de Avances")

nombres = df_unidad['Integrantes'].tolist()
if nombres:
    conquistador = st.selectbox("Integrante:", nombres)
    fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
    
    c1, c2, c3 = st.columns(3)
    nuevo_estado = {}
    requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                  "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                  "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

    desmarcados = []
    for i, r in enumerate(requisitos):
        col = c1 if i < 6 else (c2 if i < 10 else c3)
        en_db = bool(fila_persona.get(r) and str(fila_persona.get(r)).strip() != "")
        
        val = col.checkbox(r, value=en_db, key=f"v_{r}_{conquistador}")
        nuevo_estado[r] = val
        
        if en_db and not val:
            col.markdown('<span class="inline-warning">⚠️ Borrará fecha</span>', unsafe_allow_html=True)
            desmarcados.append(r)

    confirmar = True
    if desmarcados:
        st.divider()
        confirmar = st.toggle("Confirmar eliminación de datos históricos", value=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
        if not confirmar:
            st.error("Debes confirmar la eliminación de registros previos.")
        else:
            idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
            hoy = ahora_chile.strftime("%d/%m/%Y")
            ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
            logs = []
            
            with st.status("Actualizando...") as s:
                for req, check in nuevo_estado.items():
                    estaba = bool(fila_persona.get(req) and str(fila_persona.get(req)).strip() != "")
                    if check and not estaba:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                        logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                    elif not check and estaba:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                        logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                
                if logs: log_sheet.append_rows(logs)
                s.update(label="Sincronizado", state="complete")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
