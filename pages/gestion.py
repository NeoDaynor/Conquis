import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Gestión Club Lakonn", 
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

# --- ESTILOS CSS SOFT & LIGHT ---
def aplicar_estilos_claros():
    st.markdown(
        """
        <style>
        /* Ocultar elementos de Streamlit */
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        button[title="Manage app"] {display: none !important;}

        /* Fondo de Pantalla Claro y Suave */
        .stApp {
            background-color: #F8FAFC;
            color: #1E293B;
        }

        /* Título Principal Estilo Corporativo */
        .main-header {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
        }
        .main-header h1 {
            color: #0070C0 !important;
            font-weight: 800 !important;
            margin-bottom: 5px !important;
        }

        /* Tarjetas de Contenido */
        .content-card {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            margin-bottom: 25px;
        }

        /* Subtítulos */
        .stSubheader h2 {
            color: #334155 !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            border-left: 5px solid #0070C0;
            padding-left: 15px;
        }

        /* Botón Cambiar Unidad (Suave) */
        div.stButton > button[kind="secondary"] {
            background-color: #F1F5F9 !important;
            color: #475569 !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px !important;
        }

        /* Botón Sincronizar (Azul Profesional) */
        div.stButton > button[kind="primary"] {
            background-color: #0070C0 !important;
            color: white !important;
            height: 55px !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            font-size: 1.1rem !important;
            border: none !important;
        }
        
        /* Checkboxes y Labels */
        label { color: #475569 !important; font-weight: 600 !important; }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_claros()

# --- CONEXIÓN Y DATOS (Sin cambios en lógica) ---
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

# Cabecera Superior
st.markdown(f'''
    <div class="main-header">
        <h1>UNIDAD: {unidad_actual.upper()}</h1>
        <p style="color: #64748B;">Sistema de Gestión de Avances | {ahora_chile.strftime("%d/%m/%Y")}</p>
    </div>
''', unsafe_allow_html=True)

if st.button("⬅️ CAMBIAR DE UNIDAD", use_container_width=True, type="secondary"):
    st.switch_page("app.py")

st.markdown("<br>", unsafe_allow_html=True)

# Sección 1: Avance General
with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📊 Avance General de la Unidad")
    
    # Estilo de tabla: Azul sobre blanco
    st.dataframe(
        df_unidad.style.map(
            lambda v: 'background-color: #E0F2FE; color: #0369A1; font-weight: bold;' if v and str(v).strip() != "" else '', 
            subset=df_unidad.columns[3:]
        ),
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Sección 2: Registro de Datos
with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📝 Registrar o Corregir Avances")
    
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione al Conquistador:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            val_db = fila_persona.get(r)
            cumplido = bool(val_db and str(val_db).strip() != "")
            
            nuevo_estado[r] = col.checkbox(r, value=cumplido, key=f"ch_{r}_{conquistador.replace(' ', '_')}")

        st.markdown("<br><hr style='border: 0.5px solid #E2E8F0'><br>", unsafe_allow_html=True)
        
        # Sincronización
        if st.button("💾 SINCRONIZAR CAMBIOS CON LA NUBE", type="primary", use_container_width=True):
            idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
            hoy = ahora_chile.strftime("%d/%m/%Y")
            ahora = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
            logs = []
            
            with st.status("Sincronizando...", expanded=False) as s:
                for req, check in nuevo_estado.items():
                    val_actual = fila_persona.get(req)
                    ya_estaba = bool(val_actual and str(val_actual).strip() != "")
                    
                    if check and not ya_estaba:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                        logs.append([ahora, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                    elif not check and ya_estaba:
                        sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                        logs.append([ahora, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                
                sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                if logs: log_sheet.append_rows(logs)
                s.update(label="¡Cambios Guardados!", state="complete")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
