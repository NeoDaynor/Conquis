from datetime import datetime
from time import sleep

import gspread
import pandas as pd
import pytz
import streamlit as st
import plotly.express as px

from oauth2client.service_account import ServiceAccountCredentials
from streamlit.errors import StreamlitSecretNotFoundError

from ui_theme import apply_app_theme, render_hero

st.set_page_config(
    page_title="Gestion Club Lakonn",
    layout="wide",
    initial_sidebar_state="collapsed",
)

chile_tz = pytz.timezone("America/Santiago")
ahora_chile = datetime.now(chile_tz)

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py")

unidad_actual = st.session_state.get("unidad_seleccionada", "Sin unidad")
usuario_activo = st.session_state.get("user_info", {})

if "scroll_top" not in st.session_state:
    st.session_state.scroll_top = False

apply_app_theme(max_width=1280)

st.markdown(
    """
    <style>
    .st-key-dashboard_wrap,
    .st-key-registro_wrap {
        border-radius: 22px;
        padding: 20px;
        background: linear-gradient(160deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 18px 45px rgba(5, 10, 20, 0.16);
        backdrop-filter: blur(8px);
        margin-bottom: 16px;
    }

    .st-key-dashboard_wrap .section-card,
    .st-key-registro_wrap .section-card {
        background: transparent;
        border: 0;
        box-shadow: none;
        padding: 14px 18px 18px 18px;
        margin-bottom: 0;
    }

    .st-key-dashboard_wrap .section-card h3,
    .st-key-registro_wrap .section-card h3 {
        margin-top: 0.35rem;
        margin-bottom: 1rem;
    }

    .st-key-dashboard_wrap .section-card p,
    .st-key-registro_wrap .section-card p {
        margin-top: 0;
        margin-bottom: 0.4rem;
    }

    .st-key-registro_inner_wrap {
        border-radius: 18px;
        padding: 18px 18px 8px 18px;
        background: rgba(9, 20, 37, 0.52);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        margin-top: 6px;
    }

    .st-key-registro_inner_wrap .stSelectbox,
    .st-key-registro_inner_wrap .stCheckbox,
    .st-key-registro_inner_wrap .stButton {
        position: relative;
        z-index: 1;
    }

        .stExpander {
        border: 0 !important;
        background: transparent !important;
    }

    .stExpander details {
        border-radius: 22px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        background: rgba(8, 20, 38, 0.62) !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 18px 45px rgba(5, 10, 20, 0.2);
        overflow: hidden;
    }

    .stExpander summary {
        padding: 1rem 1.15rem !important;
        font-size: 1.08rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }

    .stExpander summary:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

@st.cache_data(ttl=60)
def obtener_datos_grafico():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    hoja = client.open("RequisitosConquistadores").worksheet("Amigo")
    data = hoja.get_all_values()
    if len(data) < 2: return pd.DataFrame()
    df = pd.DataFrame(data[2:], columns=data[1])
    return df.loc[:, df.columns != '']

def render_error_view(message, detail=None):
    render_hero(
        f"Registro de {unidad_actual}",
        message,
        eyebrow="Tarjeta progresiva",
        pills=[f"Unidad: {unidad_actual}", f"Usuario: {usuario_activo.get('nombre', 'Usuario')}"],
    )
    left, right = st.columns(2)
    with left:
        if st.button("Volver al menu", use_container_width=True):
            st.switch_page("pages/menu.py")
    with right:
        if st.button("Cerrar sesion", key="logout_error", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state.pop("user_info", None)
            st.switch_page("app.py")
    st.error(message)
    if detail:
        st.warning(detail)
    st.stop()


def load_sheet_snapshot(retries=3, delay_seconds=1.2):
    last_error = None
    for attempt in range(retries):
        try:
            client = get_client()
            spreadsheet = client.open("RequisitosConquistadores")
            sheet = spreadsheet.worksheet("Amigo")
            log_sheet = spreadsheet.worksheet("Log_Cambios")
            raw_data = sheet.get_all_values()
            headers = raw_data[1]
            df_full = pd.DataFrame(raw_data[2:], columns=headers)
            return {
                "sheet": sheet,
                "log_sheet": log_sheet,
                "headers": headers,
                "df_full": df_full,
            }
        except Exception as error:
            last_error = error
            if attempt < retries - 1:
                sleep(delay_seconds)
    raise last_error


try:
    snapshot = load_sheet_snapshot()
    sheet = snapshot["sheet"]
    log_sheet = snapshot["log_sheet"]
    headers = snapshot["headers"]
    df_full = snapshot["df_full"]
    st.session_state["amigo_snapshot"] = snapshot
    df_unidad = df_full[df_full["Unidad"] == unidad_actual].copy()
except StreamlitSecretNotFoundError:
    render_error_view(
        "No se encontro la configuracion de secretos para conectar Google Sheets.",
        "Configura gcp_service_account en .streamlit/secrets.toml para usar esta vista en local.",
    )
except Exception as error:
    snapshot = st.session_state.get("amigo_snapshot")
    if snapshot:
        sheet = snapshot["sheet"]
        log_sheet = snapshot["log_sheet"]
        headers = snapshot["headers"]
        df_full = snapshot["df_full"]
        df_unidad = df_full[df_full["Unidad"] == unidad_actual].copy()
        st.warning(
            "Google Sheets no respondio en este intento. Se esta mostrando la ultima informacion cargada correctamente."
        )
    else:
        render_error_view(
            "No fue posible cargar los datos de la tarjeta progresiva.",
            f"Detalle tecnico: {error}",
        )

if usuario_activo.get("rol") == "conqui":
    df_unidad = df_unidad[
        df_unidad["Integrantes"].str.strip().str.lower()
        == usuario_activo.get("usuario", "").strip().lower()
    ]

render_hero(
    f"Registro de {unidad_actual}",
    "Visualiza avances, revisa integrantes y sincroniza el progreso de la clase con la misma linea visual del panel principal.",
    eyebrow="Tarjeta progresiva / Amigo",
    pills=[f"Hola de nuevo {usuario_activo.get('nombre', '')}"
    ,f"Tu correo es {usuario_activo.get('correo', '')}"
    ,f"Te desempeñas como: {usuario_activo.get('rol', '').upper()}"
    ],
    
)

top_left, top_right = st.columns([3, 1])
with top_left:
    if st.button("Volver al menu", key="back_menu", use_container_width=True):
        st.switch_page("pages/menu.py")
with top_right:
    if st.button("Cerrar sesion", key="logout_top", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user_info", None)
        st.switch_page("app.py")

if st.session_state.scroll_top:
    st.success("Cambios guardados correctamente.")
    st.toast("Cambios guardados", icon="✅")
    st.session_state.scroll_top = False

if usuario_activo.get("rol") == "conqui":
    st.info(f"Viendo tu progreso: {usuario_activo.get('nombre')}")
else:
    st.markdown(
        '<p class="muted-note">Modo de trabajo con permisos de edicion habilitados para liderazgo y administracion.</p>',
        unsafe_allow_html=True,
    )

# =========================================================
# GRÁFICO DE AVANCE (Filtrado por Unidad)
# =========================================================
with st.expander("📊 Avance por Conquistador / Lider", expanded=True):
    if not df_unidad.empty:
        st.markdown("### 📊 Avance de la Unidad")
        
        # 1. Usamos tu lista COMPLETA de requisitos (igual que en reportes.py)
        REQUISITOS_A_GRAFICAR = [
            "Voto y Ley", "Libro año en curso", "Libro Por la gracia de Dios", "Clase Biblica",
            "Explicar la Creacion", "Explicar 10 Plagas", "Nombre 12 Tribus", "39 Libros A.T.",
            "Explicar Juan 3:16", "Explicar II Timoteo 3:16", "Explicar Efesios 6:1-3",
            "Explicar Salmo 1", "Lectura Biblica", "Visitar a alguien", "Dar alimento",
            "Proyecto ecológico/educativo", "Buen Ciudadano", "10 Cualidades / Regla de oro Mateo 7:12",
            "Himno Nacional", "Nudos y Amarras", "Explicar Daniel 1:8", "Compromiso vida saludable",
            "Dieta saludable / Preparar cuadro", "Planear y ejecutar caminata 5K",
            "Especialidad Naturaleza", "Purificar Agua", "Armar Carpa", "Cuidar cuerda / Hacer Nudos",
            "Campamento I", "10 Reglas caminata", "Señales de Pista", "Especialidad Habilidades Manuales"
        ]
        
        # 2. Nombre exacto de la columna de los niños
        COLUMNA_NOMBRES = "Integrantes"
        
        # 3. Filtramos solo las columnas que realmente existen en el DataFrame
        cols_check = [c for c in REQUISITOS_A_GRAFICAR if c in df_unidad.columns]
        
        if cols_check:
            # Creamos una copia para no afectar la tabla que se muestra abajo
            df_para_grafico = df_unidad.copy()
            
            # Calculamos el porcentaje
            df_para_grafico["Porcentaje"] = (
                df_para_grafico[cols_check].apply(lambda x: (x.astype(str).str.strip() != "").sum(), axis=1) 
                / len(cols_check)
            ) * 100
            
            # Generamos el gráfico de Plotly
            fig = px.bar(
                df_para_grafico, 
                x=COLUMNA_NOMBRES, 
                y="Porcentaje", 
                color="Porcentaje",
                color_continuous_scale="Blues",
                range_y=[0, 100],
                text=df_para_grafico["Porcentaje"].apply(lambda x: f"{x:.0f}%"),
                labels={COLUMNA_NOMBRES: f"Registro de {unidad_actual}", "Porcentaje": "% Avance"}
            )
            
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis={'categoryorder':'total descending'},
                xaxis_tickangle=-45,
                height=350,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No se encontraron las columnas de requisitos para calcular el avance.")
    
    st.markdown("---") # Separador visual


# SECCION AVANCE GENERAL
with st.expander("Cuadro Resumen de Avance General", expanded=False):
    #st.markdown('<p class="section-label">Avance general</p>', unsafe_allow_html=True)
    with st.container(key="dashboard_wrap"):
        st.markdown(
            """
            <div class="section-card">
                <span class="mini-label">Resumen</span>
                <h3>Vista consolidada por unidad</h3>
                <p>Tabla general del progreso actual filtrada segun la unidad seleccionada.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            df_unidad.style.map(
                lambda value: "background-color: rgba(159, 211, 255, 0.28); font-weight: bold;"
                if value and str(value).strip() != ""
                else "",
                subset=df_unidad.columns[3:],
            ),
            use_container_width=True,
            hide_index=True,
        )

# REGISTRO AVANCE
with st.expander("Marcar Registro de Avances de Requisitos", expanded=True):
    if usuario_activo.get("rol") != "conqui":
        #st.markdown('<p class="section-label">Registro de avances</p>', unsafe_allow_html=True)
        with st.container(key="registro_wrap"):
            st.markdown(
                """
                <div class="section-card">
                    <span class="mini-label">Edicion</span>
                    <h3>Actualizacion por integrante</h3>
                    <p>Marca o desmarca requisitos para sincronizar los avances directamente con Google Sheets.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    
            nombres = df_unidad["Integrantes"].tolist()
            if nombres:
                with st.container(key="registro_inner_wrap"):
                    conquistador = st.selectbox("Seleccione integrante", nombres)
                    fila_persona = df_unidad[df_unidad["Integrantes"] == conquistador].iloc[0]
    
                    categorias = {
                        0: {"titulo": "Generales", "items": ["Voto y Ley", "Libro año en curso", "Libro Por la gracia de Dios", "Clase Biblica"]},
                        1: {"titulo": "Descubrimiento espiritual", "items": ["Explicar la Creacion", "Explicar 10 Plagas", "Nombre 12 Tribus", "39 Libros A.T.", "Explicar Juan 3:16", "Explicar II Timoteo 3:16", "Explicar Efesios 6:1-3", "Explicar Salmo 1", "Lectura Biblica"]},
                        2: {"titulo": "Sirviendo a otros", "items": ["Visitar a alguien", "Dar alimento", "Proyecto ecológico/educativo", "Buen Ciudadano"]},
                        3: {"titulo": "Desarrollo de la amistad", "items": ["10 Cualidades / Regla de oro Mateo 7:12", "Himno Nacional"]},
                        4: {"titulo": "Salud y aptitud fisica", "items": ["Nudos y Amarras", "Explicar Daniel 1:8", "Compromiso vida saludable", "Dieta saludable / Preparar cuadro"]},
                        5: {"titulo": "Liderazgo", "items": ["Planear y ejecutar caminata 5K"]},
                        6: {"titulo": "Estudio de la naturaleza", "items": ["Especialidad Naturaleza", "Purificar Agua", "Armar Carpa"]},
                        7: {"titulo": "Arte de acampar", "items": ["Cuidar cuerda / Hacer Nudos", "Campamento I", "10 Reglas caminata", "Señales de Pista"]},
                        8: {"titulo": "Estilo de vida", "items": ["Especialidad Habilidades Manuales"]},
                    }
    
                    cols = st.columns(len(categorias))
                    nuevo_estado = {}
                    confirmaciones = {}
    
                    for col_idx, info in categorias.items():
                        with cols[col_idx]:
                            st.markdown(
                                f"<p class='mini-label' style='display:block; margin-bottom:0.55rem;'>{info['titulo']}</p>",
                                unsafe_allow_html=True,
                            )
    
                            for item in info["items"]:
                                valor_actual = bool(fila_persona.get(item) and str(fila_persona.get(item)).strip() != "")
                                key_cb = f"cb_{conquistador}_{item}"
                                marcado = st.checkbox(item, value=valor_actual, key=key_cb)
                                key_confirm_state = f"confirm_state_{key_cb}"
    
                                if key_confirm_state not in st.session_state:
                                    st.session_state[key_confirm_state] = False
    
                                if valor_actual and not marcado:
                                    with st.popover("Confirmar cambio"):
                                        st.warning("Estas quitando una marca ya registrada.")
                                        if st.button("Si, eliminar", key=f"btn_{key_cb}"):
                                            st.session_state[key_confirm_state] = True
    
                                    if st.session_state[key_confirm_state]:
                                        st.success("Confirmado para eliminar.")
    
                                    confirmaciones[item] = st.session_state[key_confirm_state]
                                else:
                                    confirmaciones[item] = True
                                    st.session_state[key_confirm_state] = False
    
                                nuevo_estado[item] = marcado
    
                    if st.button("Sincronizar cambios", type="primary", use_container_width=True):
                        try:
                            fila_idx_df = df_full[df_full["Integrantes"] == conquistador].index
                            if len(fila_idx_df) == 0:
                                st.error("No se encontro el registro en la hoja.")
                                st.stop()
    
                            fila_real = fila_idx_df[0] + 3
                            hoy = ahora_chile.strftime("%d/%m/%Y")
                            ahora_log = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")
                            updates = []
                            logs = []
                            hubo_cambios = False
    
                            with st.status("Sincronizando...") as status:
                                for requisito, marcado in nuevo_estado.items():
                                    estaba_marcado = bool(
                                        fila_persona.get(requisito) and str(fila_persona.get(requisito)).strip() != ""
                                    )
    
                                    if not marcado and estaba_marcado and not confirmaciones.get(requisito, False):
                                        continue
    
                                    if requisito in headers:
                                        col_idx = headers.index(requisito) + 1
                                        if marcado and not estaba_marcado:
                                            updates.append(
                                                {"range": gspread.utils.rowcol_to_a1(fila_real, col_idx), "values": [[hoy]]}
                                            )
                                            logs.append(
                                                [
                                                    ahora_log,
                                                    usuario_activo["nombre"],
                                                    usuario_activo["cargo"],
                                                    conquistador,
                                                    requisito,
                                                    "Marcado",
                                                ]
                                            )
                                            hubo_cambios = True
                                        elif not marcado and estaba_marcado:
                                            updates.append(
                                                {"range": gspread.utils.rowcol_to_a1(fila_real, col_idx), "values": [[""]]}
                                            )
                                            logs.append(
                                                [
                                                    ahora_log,
                                                    usuario_activo["nombre"],
                                                    usuario_activo["cargo"],
                                                    conquistador,
                                                    requisito,
                                                    "Desmarcado",
                                                ]
                                            )
                                            hubo_cambios = True
    
                                if hubo_cambios:
                                    if "Ult. Actualizacion" in headers:
                                        col_upd = headers.index("Ult. Actualizacion") + 1
                                        updates.append(
                                            {"range": gspread.utils.rowcol_to_a1(fila_real, col_upd), "values": [[hoy]]}
                                        )
    
                                    sheet.batch_update(updates)
                                    if logs:
                                        log_sheet.append_rows(logs)
    
                                    status.update(label="Guardado con exito.", state="complete")
                                else:
                                    status.update(label="No se detectaron cambios nuevos.", state="complete")
    
                            st.cache_resource.clear()
                            st.session_state.scroll_top = True
                            st.rerun()
    
                        except Exception as error:
                            st.error(f"Error critico al guardar: {error}")
    else:
        st.markdown(
            """
            <div class="section-card">
                <span class="mini-label">Visualizacion</span>
                <h4>Acceso de solo lectura</h4>
                <p>Este perfil puede revisar avances, pero no editar registros dentro de la tarjeta progresiva.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
