import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Importamos tu tema visual
try:
    from ui_theme import apply_app_theme, render_hero
except ImportError:
    def apply_app_theme(max_width): pass
    def render_hero(t, s, eyebrow): st.title(f"{eyebrow}: {t}")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel de Control - Conquistadores", layout="wide")

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

apply_app_theme(max_width=1100)

# --- CONFIGURACIÓN DE TU EXCEL ---
# ⚠️ Nombres de columnas de requisitos (Fila 2 de tu Excel)
COLUMNAS_DE_REQUISITOS = [
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

# ⚠️ NOMBRE DE LA COLUMNA DE LOS NIÑOS
COLUMNA_NOMBRES = "Integrantes" 

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def descargar_datos():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    secret_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_dict, scope)
    client = gspread.authorize(creds)
    
    hoja = client.open("RequisitosConquistadores").worksheet("Amigo")
    data = hoja.get_all_values()
    
    if len(data) < 2:
        return pd.DataFrame()
    
    # Headers en Fila 2, Datos desde Fila 3
    headers = data[1] 
    rows = data[2:]
    
    df = pd.DataFrame(rows, columns=headers)
    df = df.loc[:, df.columns != ''] # Eliminar columnas sin título
    return df

# --- UI PRINCIPAL ---
render_hero("Reporte de Progreso", "Estadísticas en tiempo real de la clase de Amigo", eyebrow="Panel de Control")

try:
    with st.spinner("Descargando datos del Club Lakonn..."):
        df = descargar_datos()

    if df.empty:
        st.warning("Aún no hay datos registrados en la hoja de Excel.")
    else:
        # --- PROCESAMIENTO DE DATOS ---
        columnas_validas = [col for col in COLUMNAS_DE_REQUISITOS if col in df.columns]
        
        if not columnas_validas:
            st.error("No se encontraron las columnas de requisitos.")
            st.write("Columnas detectadas:", list(df.columns))
            st.stop()

        # Cálculo de progreso (quitamos espacios y contamos celdas no vacías)
        df["Req_Completados"] = df[columnas_validas].apply(lambda fila: (fila.astype(str).str.strip() != "").sum(), axis=1)
        total_requisitos = len(columnas_validas)
        df["Porcentaje"] = (df["Req_Completados"] / total_requisitos) * 100

        # --- FILTROS ---
        st.markdown("### Filtros de Búsqueda")
        if "Unidad" in df.columns:
            unidades = ["Todas las Unidades"] + [u for u in df["Unidad"].unique() if str(u).strip() != ""]
            unidad_seleccionada = st.selectbox("Filtrar por Unidad:", unidades)
            if unidad_seleccionada != "Todas las Unidades":
                df = df[df["Unidad"] == unidad_seleccionada]

        # --- MÉTRICAS GLOBALES ---
        st.markdown("---")
        promedio_general = df["Porcentaje"].mean() if not df.empty else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Conquistadores Activos", len(df))
        c2.metric("Promedio de Cumplimiento", f"{promedio_general:.1f}%")
        c3.metric("Requisitos Evaluados", total_requisitos)
        st.progress(int(promedio_general) / 100)

        # --- GRÁFICOS ---
        st.markdown("---")
        st.subheader("Progreso Individual por Conquistador")
        
        # Usamos "Integrantes" para el eje X
        col_x = COLUMNA_NOMBRES if COLUMNA_NOMBRES in df.columns else df.columns[0]

        fig = px.bar(
            df, 
            x=col_x, 
            y="Porcentaje", 
            color="Porcentaje",
            color_continuous_scale="Blues",
            range_y=[0, 100], 
            text=df["Porcentaje"].apply(lambda x: f"{x:.0f}%"),
            labels={col_x: "Nombre del Niño", "Porcentaje": "% de Avance"}
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis={'categoryorder':'total descending'},
            xaxis_tickangle=-45,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- TABLA DE DETALLES ---
        st.markdown("### Detalle Exacto de Requisitos")
        with st.expander("Ver tabla completa de progreso"):
            # Evitamos duplicados en la tabla
            columnas_tabla = [col_x, "Req_Completados", "Porcentaje"]
            
            if "Unidad" in df.columns and "Unidad" not in columnas_tabla:
                columnas_tabla.insert(1, "Unidad")
            
            for req in columnas_validas:
                if req not in columnas_tabla:
                    columnas_tabla.append(req)
            
            df_vista = df[columnas_tabla].copy()
            df_vista["Porcentaje"] = df_vista["Porcentaje"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_vista, use_container_width=True)

except Exception as e:
    st.error(f"Hubo un error crítico: {e}")

# --- BOTÓN DE VOLVER ---
# --- BOTÓN DE VOLVER ---
st.markdown("---")
col_espacio1, col_boton, col_espacio2 = st.columns([1, 2, 1])

with col_boton:
    if st.button("🏠 Volver al Menú Principal", use_container_width=True):
        st.switch_page("pages/menu.py")
