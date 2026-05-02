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
# que cuentan como requisitos para la tarjeta. (Deben estar en la FILA 2 de tu Excel)
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
@st.cache_data(ttl=60) # Guarda los datos en caché por 60 segundos
def descargar_datos():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    secret_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_dict, scope)
    client = gspread.authorize(creds)
    
    # Abrimos la pestaña correcta
    hoja = client.open("RequisitosConquistadores").worksheet("Amigo")
    
    # Leemos TODO el contenido de la hoja
    data = hoja.get_all_values()
    
    if len(data) < 2:
        return pd.DataFrame() # Retorna tabla vacía si no hay suficientes datos
    
    # --- AJUSTE PARA LEER LOS TÍTULOS DESDE LA FILA 2 ---
    # data[0] es la Fila 1 de Excel (la ignoramos)
    # data[1] es la Fila 2 de Excel (aquí están tus nombres de columnas)
    headers = data[1] 
    
    # data[2:] son los datos de los niños que empiezan en la Fila 3
    rows = data[2:]
    # ----------------------------------------------------
    
    # Creamos el DataFrame de Pandas
    df = pd.DataFrame(rows, columns=headers)
    
    # Limpiamos columnas vacías que confunden al sistema
    df = df.loc[:, df.columns != '']
    
    return df

# --- UI PRINCIPAL ---
render_hero("Reporte de Progreso", "Estadísticas en tiempo real de la clase de Amigo", eyebrow="Panel de Control")

try:
    with st.spinner("Conectando con la base de datos del Club..."):
        df = descargar_datos()

    if df.empty:
        st.warning("Aún no hay datos registrados en la hoja de Excel.")
    else:
        # --- PROCESAMIENTO DE DATOS ---
        # 1. Filtramos solo las columnas de requisitos que sí existen en tu Excel
        columnas_validas = [col for col in COLUMNAS_DE_REQUISITOS if col in df.columns]
        
        # Modo Diagnóstico: Si no encuentra las columnas, te avisa por qué
        if not columnas_validas:
            st.error("No se encontraron las columnas de requisitos en tu Excel.")
            st.write("🕵️ **Python detectó estas columnas en la Fila 2 de tu Excel:**")
            st.write(list(df.columns))
            st.write("📝 **Pero tú le pediste buscar estas en el código:**")
            st.write(COLUMNAS_DE_REQUISITOS)
            st.info("💡 Revisa la lista de arriba y asegúrate de que los nombres coincidan exactamente (cuidado con los espacios invisibles al final de las palabras).")
            st.stop()

        # 2. Contamos cuántos requisitos llenó cada niño (contamos celdas que NO estén vacías)
        df["Req_Completados"] = df[columnas_validas].apply(lambda fila: (fila.astype(str).str.strip() != "").sum(), axis=1)
        
        # 3. Calculamos el porcentaje
        total_requisitos = len(columnas_validas)
        df["Porcentaje"] = (df["Req_Completados"] / total_requisitos) * 100

        # --- FILTROS ---
        st.markdown("### Filtros de Búsqueda")
        if "Unidad" in df.columns:
            # Obtenemos unidades únicas, ignorando celdas vacías
            unidades = ["Todas las Unidades"] + [u for u in df["Unidad"].unique() if str(u).strip() != ""]
            unidad_seleccionada = st.selectbox("Filtrar por Unidad:", unidades)
            
            if unidad_seleccionada != "Todas las Unidades":
                df = df[df["Unidad"] == unidad_seleccionada]
        else:
            st.info("💡 Tip: Si agregas una columna llamada 'Unidad' en tu Excel, podrás filtrar los gráficos por unidad.")

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
        
        if not df.empty:
            # Buscar la columna Nombre, o usar la primera que encuentre
            columna_nombre = "Nombre" if "Nombre" in df.columns else df.columns[0] 
            
            fig = px.bar(
                df, 
                x=columna_nombre, 
                y="Porcentaje", 
                color="Porcentaje",
                color_continuous_scale="Blues", # Colores institucionales
                range_y=[0, 100], 
                text=df["Porcentaje"].apply(lambda x: f"{x:.0f}%"), 
                labels={columna_nombre: "Conquistador", "Porcentaje": "% Completado"}
            )
            
            fig.update_traces(textposition='outside')
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            
            st.plotly_chart(fig, use_container_width=True)

        # --- TABLA DE DETALLES ---
        st.markdown("### Detalle Exacto de Requisitos")
        with st.expander("Ver tabla completa de progreso"):
            if not df.empty:
                columna_nombre = "Nombre" if "Nombre" in df.columns else df.columns[0]
                columnas_a_mostrar = [columna_nombre, "Req_Completados", "Porcentaje"] + columnas_validas
                
                if "Unidad" in df.columns:
                    columnas_a_mostrar.insert(1, "Unidad")
                
                df_vista = df[columnas_a_mostrar].copy()
                df_vista["Porcentaje"] = df_vista["Porcentaje"].apply(lambda x: f"{x:.1f}%")
                st.dataframe(df_vista, use_container_width=True)

except Exception as e:
    st.error(f"Hubo un error crítico al procesar el reporte: {e}")

# --- BOTÓN DE VOLVER ---
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Volver al Menú Principal"):
    st.switch_page("pages/menu.py")
