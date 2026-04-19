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

# ✅ INICIALIZAR VARIABLE DE SCROLL (OBLIGATORIO)
if "scroll_top" not in st.session_state:
    st.session_state.scroll_top = False

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

# --- CSS INYECTADO (RESTAURADO COMPLETAMENTE) ---
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
        div.stButton > button[kind="primary"] {{
            background-color: var(--brand-color) !important;
            color: white !important;
            height: 55px;
            font-weight: bold;
            border-radius: 10px;
            width: 100%;
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

# Leemos todos los valores (Encabezados en Fila 2)
raw_data = sheet.get_all_values()
headers = raw_data[1]
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# ✅ FILTRAR SOLO SU REGISTRO SI ES CONQUI
if usuario_activo.get("rol") == "conqui":
    df_unidad = df_unidad[
        df_unidad['Integrantes'].str.strip().str.lower() ==
        usuario_activo.get("usuario", "").strip().lower()
    ]
    
# --- HEADER ---
if st.session_state.scroll_top:
    st.success("✅ Cambios guardados correctamente")
    st.toast("Cambios guardados", icon="✅")

    # 🔥 FIX REAL PARA CELULAR Y PC
    st.markdown("""
    <script>
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 200);
    </script>
    """, unsafe_allow_html=True)

    st.session_state.scroll_top = False

st.markdown(f'<div class="header-box"><h2 style="color:var(--brand-color); margin:0;">UNIDAD: {unidad_actual.upper()}</h2></div>', unsafe_allow_html=True)

# 👇 MENSAJE SOLO PARA CONQUI
if usuario_activo.get("rol") == "conqui":
    st.markdown(f"""
    <div style="
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-color);
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-weight: 500;
        display: inline-block;
    ">
        👤 Viendo tu progreso: <b>{usuario_activo.get('nombre')}</b>
    </div>
    """, unsafe_allow_html=True)
    
if st.button("⬅️ VOLVER AL MENU"):
    st.switch_page("pages/menu.py")

# TARJETA 1: AVANCE GENERAL
with st.container():
    st.markdown("### 📊 Avance General")
    st.dataframe(
        df_unidad.style.map(lambda v: 'background-color: rgba(59, 130, 246, 0.2); font-weight: bold;' if v and str(v).strip() != "" else '', subset=df_unidad.columns[3:]),
        use_container_width=True, hide_index=True
    )

# TARJETA 2: REGISTRO DE AVANCES
if usuario_activo.get("rol") != "conqui":
    with st.container():
        st.markdown("### 📝 Registro de Avances")
        
        nombres = df_unidad['Integrantes'].tolist()
        if nombres:
            conquistador = st.selectbox("Seleccione Integrante:", nombres)
            fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
            
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
    
            cols = st.columns(len(categorias))
            nuevo_estado = {}
            confirmaciones = {}
    
            for col_idx, info in categorias.items():
                with cols[col_idx]:
                    st.markdown(f"<p style='font-size: 0.75rem; font-weight: bold; color: var(--brand-color);'>{info['titulo']}</p>", unsafe_allow_html=True)
                    
                    for item in info['items']:
                        valor_actual = bool(fila_persona.get(item) and str(fila_persona.get(item)).strip() != "")
                        key_cb = f"cb_{conquistador}_{item}"
                        marcado = st.checkbox(item, value=valor_actual, key=key_cb)
    
                        # ✅ FIX REAL: persistencia con session_state
                        key_confirm_state = f"confirm_state_{key_cb}"
    
                        if key_confirm_state not in st.session_state:
                            st.session_state[key_confirm_state] = False
    
                        if valor_actual and not marcado:
                            with st.popover("⚠️ Confirmar"):
                                st.warning("¿Seguro que deseas quitar esta marca?")
                                
                                if st.button("Sí, eliminar", key=f"btn_{key_cb}"):
                                    st.session_state[key_confirm_state] = True
    
                            if st.session_state[key_confirm_state]:
                                st.success("✔ Confirmado para eliminar")
    
                            confirmaciones[item] = st.session_state[key_confirm_state]
                        else:
                            confirmaciones[item] = True
                            st.session_state[key_confirm_state] = False
    
                        nuevo_estado[item] = marcado
    
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
                try:
                    fila_idx_df = df_full[df_full['Integrantes'] == conquistador].index
    
                    if len(fila_idx_df) == 0:
                        st.error("No se encontró el registro en la hoja.")
                        st.stop()
    
                    fila_real = fila_idx_df[0] + 3
    
                    hoy = ahora_chile.strftime("%d/%m/%Y")
                    ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                    
                    updates = []
                    logs = []
                    hubo_cambios = False
                    
                    with st.status("Sincronizando...") as s:
                        for req, marcado in nuevo_estado.items():
                            estaba_marcado = bool(fila_persona.get(req) and str(fila_persona.get(req)).strip() != "")
    
                            # 🚨 BLOQUEO SI NO CONFIRMA
                            if not marcado and estaba_marcado:
                                if not confirmaciones.get(req, False):
                                    continue
                            
                            if req in headers:
                                col_idx = headers.index(req) + 1
                                
                                if marcado and not estaba_marcado:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(fila_real, col_idx), 'values': [[hoy]]})
                                    logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Marcado"])
                                    hubo_cambios = True
                                elif not marcado and estaba_marcado:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(fila_real, col_idx), 'values': [[""]]})
                                    logs.append([ahora_log, usuario_activo['nombre'], usuario_activo['cargo'], conquistador, req, "Desmarcado"])
                                    hubo_cambios = True
                        
                        if hubo_cambios:
                            if "Ult. Actualizacion" in headers:
                                col_upd = headers.index("Ult. Actualizacion") + 1
                                updates.append({'range': gspread.utils.rowcol_to_a1(fila_real, col_upd), 'values': [[hoy]]})
                            
                            sheet.batch_update(updates)
                            if logs:
                                log_sheet.append_rows(logs)
    
                            s.update(label="¡Guardado con éxito!", state="complete")
                            st.markdown("""
                                <script>
                                var topElement = document.getElementById("top");
                                if (topElement) {
                                    topElement.scrollIntoView({ behavior: "smooth" });
                                }
                                </script>
                                """, unsafe_allow_html=True)
                        else:
                            s.update(label="No se detectaron cambios nuevos.", state="complete")
                    
                   ## st.cache_resource.clear()
                   ## st.rerun()
                    
                    st.cache_resource.clear()
                    
                    # ✅ activar flag para subir “virtualmente”
                    st.session_state.scroll_top = True
                    
                    st.rerun()
    
                except Exception as e:
                    st.error(f"Error crítico al guardar: {e}")
else:
    if usuario_activo.get("rol") == "conqui":
    st.markdown(f"""
    <div style="
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-color);
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-weight: 500;
        display: inline-block;
    ">
        👀 Solo tienes acceso a visualización.</b>
    </div>
    """, unsafe_allow_html=True)
