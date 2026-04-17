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

# --- ESTILOS CSS INTELIGENTES (Modo Claro/Oscuro y Corrección de Divs) ---
def aplicar_estilos_adaptativos():
    st.markdown(
        """
        <style>
        /* Ocultar elementos innecesarios */
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        
        /* Variables de color según el tema del sistema */
        :root {
            --bg-color: #F8FAFC;
            --card-bg: white;
            --text-main: #1E293B;
            --border-color: #E2E8F0;
            --title-color: #0070C0;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #0E1117;
                --card-bg: #1E293B;
                --text-main: #F1F5F9;
                --border-color: #334155;
                --title-color: #3B82F6;
            }
        }

        .stApp { background-color: var(--bg-color); color: var(--text-main); }

        /* Corrección de DIVS flotantes: Contenedores ajustados */
        .main-header {
            background-color: var(--card-bg); padding: 20px; border-radius: 15px;
            text-align: center; border: 1px solid var(--border-color);
            margin-bottom: 15px;
        }
        
        .content-card {
            background-color: var(--card-bg); padding: 20px; border-radius: 15px;
            border: 1px solid var(--border-color); 
            margin-bottom: 15px; /* Elimina el espacio excesivo que causaba el efecto 'flotante' */
            display: flow-root; /* Asegura que el contenedor envuelva todo su contenido */
        }

        /* Botones y Alertas */
        div.stButton > button[kind="primary"] {
            background-color: var(--title-color) !important; color: white !important;
            height: 55px !important; font-weight: bold !important; border-radius: 12px !important;
        }

        .inline-warning {
            color: #F59E0B; font-size: 0.85rem; font-weight: bold;
            display: block; margin-top: -12px; margin-bottom: 8px;
        }
        
        /* Ajuste de visibilidad de texto en tablas para modo oscuro */
        [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_adaptativos()

# --- CONEXIÓN Y DATOS ---
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

# --- INTERFAZ ADAPTADA ---
st.markdown(f'<div class="main-header"><h1 style="color:var(--title-color); margin:0;">UNIDAD: {unidad_actual.upper()}</h1></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER", type="secondary", use_container_width=True):
    st.switch_page("app.py")

# Contenedor 1: Tabla (Corregido)
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.subheader("📊 Avance General")
st.dataframe(
    df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.2); color: var(--title-color); font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
    use_container_width=True, hide_index=True
)
st.markdown('</div>', unsafe_allow_html=True)

# Contenedor 2: Registro (Corregido)
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.subheader("📝 Registro de Avances")

nombres = df_unidad['Integrantes'].tolist()
if nombres:
    conquistador = st.selectbox("Seleccione Integrante:", nombres)
    fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
    
    c1, c2, c3 = st.columns(3)
    nuevo_estado = {}
    requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                  "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                  "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

    desmarcados_detectados = []

    for i, r in enumerate(requisitos):
        col = c1 if i < 6 else (c2 if i < 10 else c3)
        val_db = fila_persona.get(r)
        ya_cumplido = bool(val_db and str(val_db).strip() != "")
        
        nuevo_val = col.checkbox(r, value=ya_cumplido, key=f"ch_{r}_{conquistador}")
        nuevo_estado[r] = nuevo_val
        
        # Alerta Inline: Inmediata debajo del check
        if ya_cumplido and not nuevo_val:
            col.markdown(f'<span class="inline-warning">⚠️ Se eliminará fecha</span>', unsafe_allow_html=True)
            desmarcados_detectados.append(r)

    st.markdown("<br>", unsafe_allow_html=True)
    
    confirmar_global = True
    if desmarcados_detectados:
        st.warning(f"Confirmación requerida para eliminar registros en: {', '.join(desmarcados_detectados)}")
        confirmar_global = st.toggle("CONFIRMO LA ELIMINACIÓN", value=False)

    if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
        if desmarcados_detectados and not confirmar_global:
            st.error("Error: Debes marcar el interruptor de confirmación para eliminar registros previos.")
        else:
            idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
            hoy = ahora_chile.strftime("%d/%m/%Y")
            ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
            logs = []
            
            with st.status("Actualizando Google Sheets...") as s:
                for req, check in nuevo_estado.items():
                    val_actual = fila_persona.get(req)
                    estaba_marcado = bool(val_actual and str(val_actual).strip() != "")
                    
                    if check and not estaba_marcado:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                        logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                    elif not check and estaba_marcado:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                        logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                
                sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                if logs: log_sheet.append_rows(logs)
                s.update(label="Sincronización Exitosa", state="complete")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
