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

# --- ESTILOS CSS SOFT (Mantenidos por tu aprobación) ---
def aplicar_estilos_claros():
    st.markdown(
        """
        <style>
        #MainMenu, footer, header, .stAppDeployButton {visibility: hidden;}
        .stApp { background-color: #F8FAFC; color: #1E293B; }
        .main-header {
            background-color: white; padding: 25px; border-radius: 15px;
            text-align: center; border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;
        }
        .main-header h1 { color: #0070C0 !important; font-weight: 800 !important; }
        .content-card {
            background-color: white; padding: 25px; border-radius: 15px;
            border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
            margin-bottom: 20px;
        }
        div.stButton > button[kind="primary"] {
            background-color: #0070C0 !important; color: white !important;
            height: 55px !important; font-weight: bold !important;
            border-radius: 12px !important; width: 100%;
        }
        /* Estilo para la Alerta Crítica */
        .warning-box {
            background-color: #FFFBEB; border-left: 5px solid #F59E0B;
            padding: 15px; border-radius: 8px; margin-bottom: 15px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

aplicar_estilos_claros()

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
st.markdown(f'<div class="main-header"><h1>UNIDAD: {unidad_actual.upper()}</h1></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER", use_container_width=True, type="secondary"):
    st.switch_page("app.py")

with st.container():
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📊 Avance General")
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: #E0F2FE; color: #0369A1; font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True, hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.container():
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

        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            val_db = fila_persona.get(r)
            cumplido = bool(val_db and str(val_db).strip() != "")
            nuevo_estado[r] = col.checkbox(r, value=cumplido, key=f"ch_{r}_{conquistador}")

        # --- LÓGICA DE ALERTA RESTAURADA ---
        desmarcados = [req for req, estado in nuevo_estado.items() if bool(fila_persona.get(req)) and not estado]
        confirmacion_borrado = True # Por defecto es True si no hay desmarcados
        
        if desmarcados:
            st.markdown(f'''
                <div class="warning-box">
                    <b style="color: #92400E;">⚠️ ATENCIÓN:</b> Estás desmarcando <b>{len(desmarcados)}</b> requisitos que ya estaban completados. 
                    Esto borrará la fecha de registro original en el sistema.
                </div>
            ''', unsafe_allow_html=True)
            confirmacion_borrado = st.toggle(f"CONFIRMO QUE DESEO ELIMINAR: {', '.join(desmarcados)}", value=False)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón con validación de alerta
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
            if desmarcados and not confirmacion_borrado:
                st.error("❌ OPERACIÓN BLOQUEADA: Debes confirmar la eliminación de los requisitos marcados en la alerta naranja.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                hoy = ahora_chile.strftime("%d/%m/%Y")
                ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                logs = []
                
                with st.status("Actualizando registros...") as s:
                    for req, check in nuevo_estado.items():
                        val_actual = fila_persona.get(req)
                        ya_estaba = bool(val_actual and str(val_actual).strip() != "")
                        
                        if check and not ya_estaba:
                            sheet.update_cell(idx_excel, headers.index(req) + 1, hoy)
                            logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                        elif not check and ya_estaba:
                            sheet.update_cell(idx_excel, headers.index(req) + 1, "")
                            logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                    
                    sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                    if logs: log_sheet.append_rows(logs)
                    s.update(label="¡Sincronización Exitosa!", state="complete")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
