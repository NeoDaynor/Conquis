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
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CSS INYECTADO DIRECTO A COMPONENTES NATIVOS ---
def aplicar_estilos_nativos():
    # Cargamos las imágenes para el fondo responsivo
    bin_str_pc = get_base64_of_bin_file('images/fondopc.jpg')
    bin_str_mob = get_base64_of_bin_file('images/fondocelu.webp')

    st.markdown(
        f"""
        <style>
        /* Ocultar elementos de sistema */
        #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
        
        /* Fondo Responsivo idéntico al Login */
        .stApp {{
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_str_pc}"); }} }}
        @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_str_mob}"); }} }}

        /* Variables según el tema del navegador con transparencia para el fondo */
        :root {{
            --bg-card: rgba(255, 255, 255, 0.95);
            --border: #0070C0;
            --text-color: #1E293B;
            --brand-color: #0070C0;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-card: rgba(30, 41, 59, 0.95);
                --border: #334155;
                --text-color: #F1F5F9;
                --brand-color: #3B82F6;
            }}
        }}

        .stApp {{ color: var(--text-color); }}

        /* SOLUCIÓN AL LOOP: Aplicar el estilo de tarjeta directamente al st.container nativo */
        [data-testid="stVerticalBlock"] > div:has(div[data-testid="stVerticalBlock"]) {{
            background-color: var(--bg-card) !important;
            padding: 20px !important;
            border-radius: 12px !important;
            border: 1px solid var(--border) !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
        }}

        .header-box {{
            background-color: var(--bg-card);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border);
            margin-bottom: 20px;
        }}

        /* Alerta Inline para móviles */
        .inline-warning {{
            color: #F59E0B;
            font-size: 0.8rem;
            font-weight: bold;
            display: block;
            margin-top: -10px;
            margin-bottom: 5px;
        }}

        /* Botón de Sincronización */
        div.stButton > button[kind="primary"] {{
            background-color: var(--brand-color) !important;
            color: white !important;
            height: 55px;
            font-weight: bold;
            border-radius: 10px;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_nativos()

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

raw_data = sheet.get_all_values()
headers = raw_data[1]
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- ESTRUCTURA DE LA PÁGINA ---

# Título de la Unidad
st.markdown(f'<div class="header-box"><h2 style="color:var(--brand-color); margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER AL MENU"):
    st.switch_page("menu.py")

# TARJETA 1: AVANCE GENERAL
with st.container():
    st.markdown("### 📊 Avance General")
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.2); color: var(--brand-color); font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True, hide_index=True
    )

# TARJETA 2: REGISTRO DE AVANCES
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
            listo_en_db = bool(fila_persona.get(r) and str(fila_persona.get(r)).strip() != "")
            
            estado_check = col.checkbox(r, value=listo_en_db, key=f"f_{r}_{conquistador}")
            nuevo_estado[r] = estado_check
            
            if listo_en_db and not estado_check:
                col.markdown('<span class="inline-warning">⚠️ Borrará fecha</span>', unsafe_allow_html=True)
                desmarcados.append(r)

        confirmacion_final = True
        if desmarcados:
            st.divider()
            confirmacion_final = st.toggle("Confirmar eliminación de registros históricos", value=False)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
            if not confirmacion_final:
                st.error("Error: Debes confirmar el borrado para proceder.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                hoy = ahora_chile.strftime("%d/%m/%Y")
                ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                logs = []
                
                with st.status("Actualizando registros...") as s:
                    for req, marcado in nuevo_estado.items():
                        estaba_marcado = bool(fila_persona.get(req) and str(fila_persona.get(req)).strip() != "")
                        if marcado and not estaba_marcado:
                            sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                            logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                        elif not marcado and estaba_marcado:
                            sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                            logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                    
                    if logs: log_sheet.append_rows(logs)
                    s.update(label="Sincronizado correctamente", state="complete")
                st.rerun()
