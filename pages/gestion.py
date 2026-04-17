import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz
import base64

# --- CONFIGURACIÓN DE PÁGINA (Fundamental para el Look) ---
st.set_page_config(
    page_title="Panel de Gestión | Club Lakonn", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- ZONA HORARIA Y SEGURIDAD (Sin cambios) ---
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]
usuario_activo = st.session_state["user_info"]

# --- FUNCIÓN DE ESTILO PARA LA TABLA (Azul Eléctrico Sutil) ---
def estilo_azul_electrico(val):
    if val and str(val).strip() != "":
        # Un azul más sofisticado para el avance
        return 'background-color: #007BFF; color: white;' 
    return ''

# --- CONEXIÓN (Mantenida igual) ---
@st.cache_resource
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

client = get_client()
spreadsheet = client.open("RequisitosConquistadores")
sheet = spreadsheet.worksheet("Amigo")
log_sheet = spreadsheet.worksheet("Log_Cambios") 

# --- INYECCIÓN DE CSS (El corazón del rediseño) ---
def aplicar_estilos_premium():
    # Usamos una textura de fibra de carbono oscura profesional para el fondo
    st.markdown(
        """
        <style>
        /* Ocultar elementos de Streamlit */
        #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
        button[title="Manage app"] {{display: none !important;}}

        /* FONDO: Fibra de Carbono Oscura */
        .stApp {{
            background-color: #121212;
            background-image: 
                linear-gradient(rgba(18, 18, 18, 0.95), rgba(18, 18, 18, 0.95)),
                url("data:image/svg+xml,%3Csvg width='100' height='20' viewBox='0 0 100 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M21.184 20c.35.13.72.214 1.114.214 1.704 0 3.086-1.382 3.086-3.086s-1.382-3.086-3.086-3.086c-1.704 0-3.086 1.382-3.086 3.086 0 1.056.54 1.996 1.36 2.56.24.162.492.3.76.412zm0-20c.35-.13.72-.214 1.114-.214 1.704 0 3.086 1.382 3.086 3.086S24 6.172 22.298 6.172 19.212 4.79 19.212 3.086c0-1.056.54-1.996 1.36-2.56.24-.162.492-.3.76-.412zM0 10c0 1.704 1.382 3.086 3.086 3.086 1.704 0 3.086-1.382 3.086-3.086S4.79 6.914 3.086 6.914C1.382 6.914 0 8.296 0 10zm100 0c0-1.704-1.382-3.086-3.086-3.086-1.704 0-3.086 1.382-3.086 3.086 0 1.704 1.382 3.086 3.086 3.086S100 11.704 100 10z' fill='%23282828' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
            background-attachment: fixed;
            color: #E0E0E0;
        }}

        /* CABECERA: Glassmorphism Título */
        .glass-header {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            margin-bottom: 25px;
        }}
        .glass-header h1 {{ color: white !important; font-size: 2.8em !important; font-weight: 900 !important; text-transform: uppercase; }}
        .glass-header h1 span {{ color: #007BFF; }}

        /* CONTENEDORES: Glassmorphism Tarjetas */
        .glass-card {{
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(8px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(0, 123, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            margin-bottom: 30px;
        }}

        /* Títulos de secciones */
        .stSubheader h2 {{ color: #007BFF !important; font-weight: bold !important; font-size: 1.8em !important; margin-bottom: 10px; }}
        .stSubheader p {{ color: rgba(255, 255, 255, 0.7) !important; font-size: 1.1em; }}

        /* TABLA: Limpieza Visual */
        [data-testid="stDataFrame"] {{
            background-color: transparent !important;
            padding: 5px;
        }}
        [data-testid="stDataFrame"] > div:first-child {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        [data-testid="stDataFrame"] .stDataFrameColHeaderCell, [data-testid="stDataFrame"] .stDataFrameIndexCell {{
            color: white !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
            font-weight: bold;
        }}
        [data-testid="stDataFrame"] .stDataFrameRowCell {{
            color: rgba(255, 255, 255, 0.9) !important;
        }}

        /* BOTONES PREMIUM */
        div.stButton > button {{
            border-radius: 10px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }}
        /* Botón Cambiar Unidad (Sutil) */
        div.stButton > button.stButton--secondary {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: rgba(255, 255, 255, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        div.stButton > button.stButton--secondary:hover {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }}
        /* Botón Sincronizar (Acción Principal - Verde Profundo) */
        div.stButton > button.stButton--primary {{
            background-color: #28a745 !important;
            color: white !important;
            border: 1px solid transparent !important;
            height: 60px !important;
            font-size: 1.3em !important;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        }}
        div.stButton > button.stButton--primary:hover {{
            background-color: #218838 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.5);
        }}

        /* TEXTO GENERAL */
        label {{ color: rgba(255, 255, 255, 0.8) !important; }}
        div[data-testid="stMarkdownContainer"] p {{ color: rgba(255, 255, 255, 0.9); }}
        div.stSelectbox label, div.stMultiSelect label {{ color: #007BFF !important; }}

        /* CHECKBOXES Premium (Estilo iOS) */
        [data-testid="stCheckbox"] label span:first-child {{
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 5px;
        }}
        [data-testid="stCheckbox"] input:checked + label span:first-child {{
            background-color: #007BFF !important;
            border-color: #007BFF !important;
        }}
        
        /* Expander Ajustado */
        [data-testid="stExpander"] {{
            background: rgba(255, 255, 255, 0.02) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}
        [data-testid="stExpander"] div.stSubheader h2 {{
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 1.4em !important;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_premium()

# --- DATOS (Mantenidos igual) ---
raw_data = sheet.get_all_values()
headers = raw_data[1]
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- INTERFAZ PREMIUM ---

# 1. Cabecera (Glass Título)
st.markdown(
    f"""
    <div class="glass-header">
        <h1>PANEL <span>{unidad_actual.upper()}</span></h1>
        <p>Integrantes Activos: {len(df_unidad)} | Fecha de Control: {ahora_chile.strftime("%d/%m/%Y")}</p>
    </div>
    """, 
    unsafe_allow_html=True
)

if st.button("⬅️ VOLVER A SELECCIÓN DE UNIDAD", use_container_width=True, type="secondary"):
    st.switch_page("app.py")

# 2. Contenedor: Avance General
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col_icon, col_text = st.columns([1, 15])
    with col_icon: st.markdown("# 📊")
    with col_text: st.subheader("Resumen de Avance", "Visualiza rápidamente el progreso de cada integrante en la unidad.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.dataframe(
        df_unidad.style.map(estilo_azul_electrico, subset=df_unidad.columns[3:]),
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Contenedor: Registro y Corrección
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col_icon_2, col_text_2 = st.columns([1, 15])
    with col_icon_2: st.markdown("# 📝")
    with col_text_2: st.subheader("Control de Avance", "Selecciona un integrante para registrar nuevos requisitos o corregir registros anteriores.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione al Integrante de la Unidad:", nombres)
        st.markdown("<br>", unsafe_allow_html=True)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            valor_db = fila_persona.get(r)
            esta_cumplido = bool(valor_db and str(valor_db).strip() != "")
            
            # Requisito con formato premium
            st_req = f"<span style='color: white; font-weight: bold;'>{r}</span>"
            val = col.checkbox(st_req, value=esta_cumplido, key=f"ch_{r}_{conquistador.replace(' ', '_')}")
            nuevo_estado[r] = val
            
            if esta_cumplido and not val:
                col.caption(f"<span style='color: #FFC107;'>⚠️ Se eliminará registro</span>", unsafe_allow_html=True)

        # --- SINCRONIZACIÓN Y AUDITORÍA ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        desmarcados = [req for req, estado in nuevo_estado.items() if bool(fila_persona.get(req)) and not estado]
        confirmar = True
        
        # Botón de Sincronización (Tipo Primary - Verde)
        sync_btn_col1, sync_btn_col2, sync_btn_col3 = st.columns([2, 5, 2])
        with sync_btn_col2:
            if st.button("💾 SINCRONIZAR Y REGISTRAR CAMBIOS", type="primary
