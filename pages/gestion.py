import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import pytz
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión - Club Lakonn", layout="wide")

# --- ZONA HORARIA SANTIAGO ---
chile_tz = pytz.timezone('America/Santiago')
ahora_chile = datetime.now(chile_tz)

# --- SEGURIDAD DE ACCESO ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]
usuario_activo = st.session_state["user_info"]

# --- FUNCIONES DE ESTILO (LOOK LOGIN.PY) ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def aplicar_look_login():
    bin_pc = get_base64('images/fondopc.jpg')
    bin_mob = get_base64('images/fondocelu.webp')
    
    st.markdown(
        f"""
        <style>
        /* Esconder menús de Streamlit y Git */
        #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
        button[title="Manage app"] {{display: none !important;}}
        .stAppToolbar {{display: none !important;}}

        /* Fondo Adaptativo */
        .stApp {{
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
        @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}

        /* Estilo Tarjeta Blanca (Look Login) */
        .gestion-card {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid #0070C0 !important;
            padding: 25px !important;
            border-radius: 20px !important;
            box-shadow: 0px 8px 25px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }}

        /* Texto Oscuro para lectura sobre blanco */
        .stMarkdown p, label, h1, h2, h3, h4, .stSubheader {{
            color: #1E1E1E !important;
            font-weight: bold !important;
        }}
        
        /* Ajuste de Tabla para que no rompa el fondo */
        [data-testid="stDataFrame"] {{
            background-color: white !important;
            border-radius: 10px;
            padding: 10px;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_look_login()

# --- ESTILO TABLA ---
def estilo_azul(val):
    if val and str(val).strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

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

# --- DATOS ---
raw_data = sheet.get_all_values()
headers = raw_data[1]
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---
# Título con sombra blanca para resaltar sobre el fondo oscuro del club
st.markdown(f"<h1 style='text-align: center; color: white; text-shadow: 2px 2px 4px #000;'>🛡️ UNIDAD: {unidad_actual.upper()}</h1>", unsafe_allow_html=True)

if st.button("⬅️ CAMBIAR UNIDAD", use_container_width=True):
    st.switch_page("app.py")

# --- CONTENEDOR PRINCIPAL (LOOK LOGIN) ---
with st.container():
    st.markdown('<div class="gestion-card">', unsafe_allow_html=True)
    
    st.subheader("📊 Avance General")
    st.dataframe(
        df_unidad.style.map(estilo_azul, subset=df_unidad.columns[3:]),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()

    # REGISTRO Y CORRECCIÓN 
    st.subheader("📝 Registrar o Corregir Avances")
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione al Conquistador:", nombres)
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
            
            val = col.checkbox(r, value=esta_cumplido, key=f"ch_{r}_{conquistador.replace(' ', '_')}")
            nuevo_estado[r] = val
            
            if esta_cumplido and not val:
                col.caption(f"⚠️ Se eliminará: {r}")

        # --- SINCRONIZACIÓN Y AUDITORÍA ---
        desmarcados = [req for req, estado in nuevo_estado.items() if bool(fila_persona.get(req)) and not estado]
        confirmar = True
        if desmarcados:
            st.warning("⚠️ Hay requisitos marcados que vas a eliminar.")
            confirmar = st.toggle("Confirmar eliminación", key="toggle_del")

        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary", use_container_width=True):
            if desmarcados and not confirmar:
                st.error("Debes confirmar la eliminación antes de sincronizar.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                ahora = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                hoy = ahora_chile.strftime("%d/%m/%Y")
                
                logs_a_insertar = []
                
                with st.status("Actualizando y registrando auditoría...") as s:
                    for req, check in nuevo_estado.items():
                        c_idx = headers.index(req) + 1
                        val_actual = fila_persona.get(req)
                        
                        cambio_detectado = False
                        accion = ""
                        
                        if check and not bool(val_actual):
                            sheet.update_cell(idx_excel, c_idx, hoy)
                            cambio_detectado = True
                            accion = "Marcado"
                        elif not check and bool(val_actual):
                            sheet.update_cell(idx_excel, c_idx, "")
                            cambio_detectado = True
                            accion = "Desmarcado"
                        
                        if cambio_detectado:
                            logs_a_insertar.append([
                                ahora, 
                                usuario_activo['nombre'], 
                                usuario_activo['cargo'], 
                                conquistador, 
                                req, 
                                accion
                            ])
                            
                    sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                    
                    if logs_a_insertar:
                        log_sheet.append_rows(logs_a_insertar)
                        
                    s.update(label="¡Cambios y Log guardados!", state="complete")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
