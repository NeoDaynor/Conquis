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
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

bin_pc = get_base64_of_bin_file('images/fondopc.jpg')
bin_mob = get_base64_of_bin_file('images/fondocelu.webp')

# --- CSS INYECTADO ---
def aplicar_estilos_nativos(img_pc, img_mob):
    st.markdown(
        f"""
        <style>
        #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
        .stApp {{
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{img_pc}"); }} }}
        @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{img_mob}"); }} }}
        
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
        .inline-warning {{
            color: #F59E0B;
            font-size: 0.8rem;
            font-weight: bold;
            display: block;
            margin-top: -10px;
            margin-bottom: 5px;
        }}
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

aplicar_estilos_nativos(bin_pc, bin_mob)

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
headers = raw_data[1]  # Fila 2
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- ESTRUCTURA DE LA PÁGINA ---
st.markdown(f'<div class="header-box"><h2 style="color:var(--brand-color); margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

if st.button("⬅️ VOLVER AL MENU"):
    st.switch_page("pages/menu.py")

# TARJETA 1: AVANCE GENERAL
with st.container():
    st.markdown("### 📊 Avance General")
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.2); color: #1E293B; font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True, hide_index=True
    )

# TARJETA 2: REGISTRO DE AVANCES
with st.container():
    st.markdown("### 📝 Registro de Avances")
    
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione Integrante:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        cols = st.columns(9)
        nuevo_estado = {}

        categorias = {
            0: {"titulo": "GENERALES", "items": ["Voto y Ley", "Libro año en curso", "Libro Por la gracia de Dios", "Clase Biblica"]},
            1: {"titulo": "DESCUBRIMIENTO ESPIRITUAL", "items": ["Explicar la Creacion", "Explicar 10 Plagas", "Nombre 12 Tribus", "39 Libros A.T.", "Explicar Juan 3:16", "Explicar II Timoteo 3:16","Explicar Efesios 6:1-3", "Explicar Salmo 1", "Lectura Biblica"]},
            2: {"titulo": "SIRVIENDO A OTROS", "items": ["Visitar a alguien", "Dar alimento", "Proyecto ecológico/educativo", "Buen Ciudadano"]},
            3: {"titulo": "DESARROLLO DE LA AMISTAD", "items": ["10 Cualidades / Regla de oro Mateo 7:12", "Himno Nacional"]},
            4: {"titulo": "SALUD Y APTITUD FÍSICA", "items": ["Nudos y Amarras", "Explicar Daniel 1:8", "Compromiso vida saludable", "Dieta saludable / Preparar cuadro"]},
            5: {"titulo": "LIDERAZGO", "items": ["Planear y ejecutar caminata 5K"]},
            6: {"titulo": "ESTUDIO DE LA NATURALEZA", "items": ["Especialidad Naturaleza", "Purificar Agua", "Armar Carpa"]},
            7: {"titulo": "ARTE DE ACAMPAR", "items": ["Cuidar cuerda / Hacer Nudos", "Campamento I", "10 Reglas caminata", "Señales de Pista"]},
            8: {"titulo": "ESTILO DE VIDA", "items": ["Especialidad Habilidades Manuales"]}
        }

        desmarcados = []

        for col_idx, info in categorias.items():
            col = cols[col_idx]
            col.markdown(f"<p style='font-size: 0.75rem; font-weight: bold; color: var(--brand-color); margin-bottom: 5px; height: 35px;'>{info['titulo']}</p>", unsafe_allow_html=True)
            for r in info['items']:
                listo_en_db = bool(fila_persona.get(r) and str(fila_persona.get(r)).strip() != "")
                estado_check = col.checkbox(r, value=listo_en_db, key=f"f_{r}_{conquistador}")
                nuevo_estado[r] = estado_check
                if listo_en_db and not estado_check:
                    col.markdown('<span class="inline-warning">⚠️ Borrará fecha</span>', unsafe_allow_html=True)
                    desmarcados.append(r)

        confirmacion_final = not bool(desmarcados)
        if desmarcados:
            st.divider()
            confirmacion_final = st.toggle("Confirmar eliminación de registros históricos", value=False)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
            if not confirmacion_final:
                st.error("Error: Debes confirmar el borrado para proceder.")
            else:
                try:
                    # LOCALIZACIÓN INFALIBLE DE LA FILA (Buscamos el nombre en la lista original de Sheet)
                    nombres_col = [r[headers.index('Integrantes')] for r in raw_data]
                    fila_real_index = nombres_col.index(conquistador) + 1 # +1 porque gspread es base 1
                    
                    hoy = ahora_chile.strftime("%d/%m/%Y")
                    ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                    
                    updates = []
                    logs = []
                    hubo_cambios = False
                    
                    with st.status("Sincronizando...") as status:
                        for req, marcado in nuevo_estado.items():
                            estaba_marcado = bool(fila_persona.get(req) and str(fila_persona.get(req)).strip() != "")
                            col_idx = headers.index(req) + 1
                            
                            if marcado and not estaba_marcado:
                                updates.append({'range': gspread.utils.rowcol_to_a1(fila_real_index, col_idx), 'values': [[hoy]]})
                                logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                                hubo_cambios = True
                            elif not marcado and estaba_marcado:
                                updates.append({'range': gspread.utils.rowcol_to_a1(fila_real_index, col_idx), 'values': [[""]]})
                                logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                                hubo_cambios = True
                        
                        if hubo_cambios:
                            # Actualizar Ult. Actualización
                            col_upd = headers.index("Ult. Actualizacion") + 1
                            updates.append({'range': gspread.utils.rowcol_to_a1(fila_real_index, col_upd), 'values': [[hoy]]})
                            
                            # EJECUCIÓN EN BATCH (Súper rápido y seguro)
                            sheet.batch_update(updates)
                            if logs: log_sheet.append_rows(logs)
                            
                        status.update(label="¡Cambios guardados!", state="complete")
                    
                    st.cache_resource.clear()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error crítico: {e}")
