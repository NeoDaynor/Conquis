import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Gestión de Unidades | Club Lakonn", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- SEGURIDAD Y ZONA HORARIA ---
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]
usuario_activo = st.session_state["user_info"]

# --- ESTILOS CSS PROFESIONALES ---
def aplicar_estilos_v3():
    st.markdown(
        """
        <style>
        /* Ocultar menús de desarrollo */
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        button[title="Manage app"] {display: none !important;}

        /* Fondo de Fibra de Carbono Dark */
        .stApp {
            background-color: #0e1117;
            background-image: radial-gradient(#1e293b 0.5px, transparent 0.5px);
            background-size: 24px 24px;
        }

        /* Tarjeta Glassmorphism */
        .main-card {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
            margin-bottom: 30px;
        }

        /* Títulos */
        .main-title {
            text-align: center;
            color: #3b82f6;
            font-size: 3rem !important;
            font-weight: 800 !important;
            letter-spacing: -1px;
            margin-bottom: 0px;
            text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }

        /* Botón de Sincronización */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            border: none !important;
            height: 55px !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
        }
        
        /* Ajuste de DataFrame */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_v3()

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

# --- DISEÑO DE PANTALLA ---
st.markdown(f'<h1 class="main-title">UNIDAD {unidad_actual.upper()}</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #94a3b8;">Sistema de Gestión | {ahora_chile.strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

if st.button("⬅️ CAMBIAR UNIDAD", use_container_width=True):
    st.switch_page("app.py")

# Panel Principal
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.subheader("📊 Avance General")
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: #1d4ed8; color: white;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br><hr style='border: 0.5px solid rgba(255,255,255,0.1)'><br>", unsafe_allow_html=True)
    
    st.subheader("📝 Registrar Avances")
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccionar Conquistador:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            esta_cumplido = bool(fila_persona.get(r) and str(fila_persona.get(r)).strip() != "")
            nuevo_estado[r] = col.checkbox(r, value=esta_cumplido, key=f"ch_{r}_{conquistador.replace(' ', '_')}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary", use_container_width=True):
            idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
            hoy = ahora_chile.strftime("%d/%m/%Y")
            ahora = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
            logs = []
            
            with st.status("Sincronizando con Google Sheets...") as s:
                for req, check in nuevo_estado.items():
                    val_actual = fila_persona.get(req)
                    cumple_actual = bool(val_actual and str(val_actual).strip() != "")
                    
                    if check and not cumple_actual:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                        logs.append([ahora, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                    elif not check and cumple_actual:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                        logs.append([ahora, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                
                if logs:
                    log_sheet.append_rows(logs)
                s.update(label="Sincronización Exitosa", state="complete")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
