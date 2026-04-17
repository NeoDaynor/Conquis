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

# --- ESTILOS CSS ADAPTATIVOS Y CORRECCIÓN DE DIVS ---
def aplicar_estilos():
    st.markdown(
        """
        <style>
        /* Ocultar header y footer */
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        
        /* Paleta de colores dinámica */
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

        /* CORRECCIÓN RADICAL: Estilo directo a los contenedores de Streamlit */
        /* Seleccionamos los bloques verticales para que actúen como tarjetas */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
            background-color: var(--bg-card) !important;
            padding: 25px !important;
            border-radius: 15px !important;
            border: 1px solid var(--border) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
            margin-bottom: 20px !important;
        }

        /* Título de Unidad */
        .unidad-title {
            text-align: center;
            background-color: var(--bg-card);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
        }

        /* Alerta Inline debajo del Checkbox */
        .inline-warning {
            color: #F59E0B;
            font-size: 0.8rem;
            font-weight: bold;
            display: block;
            margin-top: -12px;
            margin-bottom: 5px;
        }
        
        /* Ajuste de Botones */
        div.stButton > button[kind="primary"] {
            background-color: var(--accent) !important;
            color: white !important;
            height: 50px;
            font-weight: bold;
            width: 100%;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos()

# --- DATOS ---
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

st.markdown(f'<div class="unidad-title"><h2 style="color:var(--accent); margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER AL PANEL"):
    st.switch_page("app.py")

# CONTENEDOR 1: AVANCE GENERAL (Ahora envuelve correctamente)
with st.container():
    st.markdown("### 📊 Avance General de Unidad")
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.2); color: var(--accent); font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True, hide_index=True
    )

# CONTENEDOR 2: REGISTRO (Ahora envuelve correctamente)
with st.container():
    st.markdown("### 📝 Registro de Avances")
    
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione Integrante:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        desmarcados = []
        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            estaba_listo = bool(fila_persona.get(r) and str(fila_persona.get(r)).strip() != "")
            
            check = col.checkbox(r, value=estaba_listo, key=f"re_{r}_{conquistador}")
            nuevo_estado[r] = check
            
            if estaba_listo and not check:
                col.markdown('<span class="inline-warning">⚠️ Borrará fecha</span>', unsafe_allow_html=True)
                desmarcados.append(r)

        confirmar = True
        if desmarcados:
            st.divider()
            confirmar = st.toggle(f"Confirmar eliminación de registros previos", value=False)
        
        st.write("") # Espaciador
        
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
            if not confirmar:
                st.error("Por favor, confirma el borrado de datos en el interruptor de arriba.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                hoy = ahora_chile.strftime("%d/%m/%Y")
                ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                logs = []
                
                with st.status("Guardando...") as s:
                    for req, marcado in nuevo_estado.items():
                        en_db = bool(fila_persona.get(req) and str(fila_persona.get(req)).strip() != "")
                        if marcado and not en_db:
                            sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                            logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                        elif not marcado and en_db:
                            sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                            logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                    
                    if logs: log_sheet.append_rows(logs)
                    s.update(label="Sincronizado", state="complete")
                st.rerun()
