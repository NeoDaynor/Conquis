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

if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]
usuario_activo = st.session_state["user_info"]

# --- ESTILOS CSS REFORZADOS ---
def aplicar_estilos_finales():
    st.markdown(
        """
        <style>
        /* Ocultar basura visual de Streamlit */
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        
        /* Variables dinámicas por tema */
        :root {
            --bg-color: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #1E293B;
            --border-color: #E2E8F0;
            --accent: #0070C0;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #0E1117;
                --card-bg: #1E293B;
                --text-main: #F1F5F9;
                --border-color: #334155;
                --accent: #3B82F6;
            }
        }

        .stApp { background-color: var(--bg-color); color: var(--text-main); }

        /* ELIMINACIÓN DE DIVS FLOTANTES: Forzamos el colapso de márgenes de Streamlit */
        [data-testid="stVerticalBlock"] > div {
            padding: 0px !important;
            gap: 0px !important;
        }

        .main-header {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .content-card {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-top: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        /* Ajuste de Botones */
        div.stButton > button {
            width: 100% !important;
            border-radius: 10px !important;
        }
        
        div.stButton > button[kind="primary"] {
            background-color: var(--accent) !important;
            color: white !important;
            height: 50px;
            font-weight: bold;
        }

        /* Alerta Inline */
        .inline-warning {
            color: #F59E0B;
            font-size: 0.8rem;
            font-weight: bold;
            display: block;
            margin-top: -10px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_finales()

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

# --- ESTRUCTURA DE PÁGINA SIN ESPACIOS MUERTOS ---

st.markdown(f'<div class="main-header"><h2 style="color:var(--accent); margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER AL PANEL"):
    st.switch_page("app.py")

# Bloque 1: Tabla de Avance
with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<p style="font-weight:bold; margin-bottom:10px;">📊 Avance General de Unidad</p>', unsafe_allow_html=True)
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.15); color: var(--accent); font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True, hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Bloque 2: Registro de Datos
with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<p style="font-weight:bold; margin-bottom:10px;">📝 Registrar Avances</p>', unsafe_allow_html=True)
    
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Integrante:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        desmarcados = []
        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            cumplido_antes = bool(fila_persona.get(r) and str(fila_persona.get(r)).strip() != "")
            
            val = col.checkbox(r, value=cumplido_antes, key=f"check_{r}_{conquistador}")
            nuevo_estado[r] = val
            
            if cumplido_antes and not val:
                col.markdown('<span class="inline-warning">⚠️ Borrará fecha</span>', unsafe_allow_html=True)
                desmarcados.append(r)

        if desmarcados:
            st.divider()
            confirmar = st.toggle(f"Confirmar borrado de: {', '.join(desmarcados)}", value=False)
        else:
            confirmar = True

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
            if not confirmar:
                st.error("Debes confirmar el borrado para continuar.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                hoy = ahora_chile.strftime("%d/%m/%Y")
                ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                logs = []
                
                with st.status("Sincronizando...") as s:
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
