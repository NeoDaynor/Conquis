import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Importamos tu tema visual (si usas ui_theme)
try:
    from ui_theme import apply_app_theme, render_hero
except ImportError:
    # Por si no tienes el ui_theme en esta página, definimos un fallback
    def apply_app_theme(max_width): pass
    def render_hero(t, s, eyebrow): st.title(f"{eyebrow}: {t}")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel de Control - Conquistadores", layout="wide")

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

apply_app_theme(max_width=1100)

# --- CONFIGURACIÓN DE TU EXCEL ---
# ⚠️ IMPORTANTE: Pon aquí los nombres EXACTOS de las columnas de tu Excel 
# que cuentan como requisitos para la tarjeta.
COLUMNAS_DE_REQUISITOS = [
    "Carnet", 
    "Fotos", 
    "Voto", 
    "Ley", 
    "Libro_Club", 
    "Camino_Cristo", 
    "Gema_Biblica"
]

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_data(ttl=60) # Guarda los datos en caché por 60 segundos para que sea rapidísimo
def descargar_datos():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    secret_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_dict, scope)
    client = gspread.authorize(creds)
    
    # ⚠️ Asegúrate de que el nombre de la hoja sea el correcto (Ej: "Amigo")
    hoja = client.open("RequisitosConquistadores").worksheet("Amigo")
    
    # Obtenemos todos los datos y los convertimos en un DataFrame de Pandas
    registros = hoja.get_all_records()
    return pd.DataFrame(registros)

# --- UI PRINCIPAL ---
render_hero("Reporte de Progreso", "Estadísticas en tiempo real de la clase de Amigo", eyebrow="Panel de Control")

try:
    with st.spinner("Conectando con la base de datos del Club..."):
        df = descargar_datos()

    if df.empty:
        st.warning("Aún no hay datos registrados en la hoja de Excel.")
    else:
        # --- PROCESAMIENTO MÁGICO DE DATOS ---
        # 1. Filtramos solo las columnas de requisitos que sí existen en tu Excel
        columnas_validas = [col for col in COLUMNAS_DE_REQUISITOS if col in df.columns]
        
        if not columnas_validas:
            st.error("No se encontraron las columnas de requisitos en tu Excel. Revisa los nombres en el código.")
            st.stop()

        # 2. Contamos cuántos requisitos llenó cada niño (contamos celdas que NO estén vacías)
        df["Req_Completados"] = df[columnas_validas].apply(lambda fila: (fila.astype(str).str.strip() != "").sum(), axis=1)
        
        # 3. Calculamos el porcentaje
        total_requisitos = len(columnas_validas)
        df["Porcentaje"] = (df["Req_Completados"] / total_requisitos) * 100

        # --- FILTROS (Si tienes columna "Unidad", la usamos) ---
        st.markdown("### Filtros de Búsqueda")
        if "Unidad" in df.columns:
            unidades = ["Todas las Unidades"] + list(df["Unidad"].unique())
            unidad_seleccionada = st.selectbox("Filtrar por Unidad:", unidades)
            
            if unidad_seleccionada != "Todas las Unidades":
                df = df[df["Unidad"] == unidad_seleccionada]
        else:
            st.info("💡 Tip: Si agregas una columna llamada 'Unidad' en tu Excel, podrás filtrar por unidades aquí.")

        # --- MÉTRICAS GLOBALES ---
        st.markdown("---")
        promedio_general = df["Porcentaje"].mean()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Conquistadores Activos", len(df))
        c2.metric("Promedio de Cumplimiento", f"{promedio_general:.1f}%")
        c3.metric("Requisitos Evaluados", total_requisitos)

        st.progress(int(promedio_general) / 100)

        # --- GRÁFICOS ---
        st.markdown("---")
        st.subheader("Progreso Individual por Conquistador")
        
        # Asegurarnos de que existe la columna "Nombre" para el gráfico
        columna_nombre = "Nombre" if "Nombre" in df.columns else df.columns[0] # Usa la primera columna si no hay "Nombre"
        
        # Gráfico de barras usando Plotly
        fig = px.bar(
            df, 
            x=columna_nombre, 
            y="Porcentaje", 
            color="Porcentaje",
            color_continuous_scale="Blues", # Un color azul institucional
            range_y=[0, 100], 
            text=df["Porcentaje"].apply(lambda x: f"{x:.0f}%"), # Muestra el % arriba de la barra
            labels={columna_nombre: "Conquistador", "Porcentaje": "% Completado"}
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        
        st.plotly_chart(fig, use_container_width=True)

        # --- TABLA DE DETALLES ---
        st.markdown("### Detalle Exacto de Requisitos")
        with st.expander("Ver tabla completa de los niños"):
            # Mostramos una tabla más limpia
            columnas_a_mostrar = [columna_nombre, "Req_Completados", "Porcentaje"] + columnas_validas
            if "Unidad" in df.columns:
                columnas_a_mostrar.insert(1, "Unidad")
            
            # Limpiamos el dataframe para la vista
            df_vista = df[columnas_a_mostrar].copy()
            df_vista["Porcentaje"] = df_vista["Porcentaje"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_vista, use_container_width=True)

except Exception as e:
    st.error(f"Hubo un error al procesar el reporte: {e}")

# --- BOTÓN DE VOLVER ---
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Volver al Menú Principal"):
    st.switch_page("pages/menu.py")
