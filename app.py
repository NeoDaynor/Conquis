import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE INFRAESTRUCTURA (GCP) ---
def get_gspread_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return None

client = get_gspread_client()
if client:
    sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Clase Amigo", layout="wide")

# --- 3. LÓGICA DE ESTILO (HEATMAP) ---
def estilo_heatmap(val):
    if val and str(val).strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# --- 4. PROCESAMIENTO DE DATOS ---
if client:
    data = sheet.get_all_values()
    headers = data[1]  # Fila 2: Nombres de columnas reales
    df_base = pd.DataFrame(data[2:], columns=headers)

    # MAPEO PARA DASHBOARD
    mapeo_items = {
        "Item1": ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis"],
        "Item2": ["Éxodo", "Levítico", "Gemas Bíblicas"],
        "Item3": ["Salmo 23 o 46", "Personaje AT"],
        "Item4": ["2 Horas Ayuda Comunitaria", "Buen Ciudadano"],
        "Item5": ["Cuestionario Historia", "Daniel 1:8", "Temperancia de Daniel"],
        "Item6": ["Menú Vegetariano"],
        "Item7": ["Especialidad Natación I", "Especialidad Naturaleza", "Flores e Insectos"],
        "Item8": ["Nudos Básicos", "Nudos Avanzados", "Pernoctar Campamento", "Examen Seguridad"],
        "Item9": ["Armar Carpa"]
    }

    df_dash = df_base[['Integrantes', 'Ult. Actualizacion']].copy()
    for item, preguntas in mapeo_items.items():
        for i, p_real in enumerate(preguntas):
            id_visual = f"{item}_P{i+1}"
            df_dash[id_visual] = df_base[p_real] if p_real in df_base.columns else ""

    # --- 5. INTERFAZ DE USUARIO ---
    st.title("🛡️ Sistema de Gestión: Clase de Amigo")
    st.markdown("### 📊 Cuadro de Cumplimiento")
    st.dataframe(
        df_dash.style.map(estilo_heatmap, subset=df_dash.columns[2:]),
        use_container_width=True, 
        hide_index=True
    )

    st.divider()

    # --- 6. SISTEMA DE ACTUALIZACIÓN (CON FUNCIÓN DE BORRADO) ---
    with st.expander("📝 Registrar o Corregir Avances"):
        conquistador = st.selectbox("Seleccione al Conquistador:", df_base['Integrantes'].tolist())
        
        # Obtener los datos actuales del conquistador seleccionado para pre-marcar los checks
        fila_datos = df_base[df_base['Integrantes'] == conquistador].iloc[0]
        
        st.info("Nota: Desmarcar un requisito también lo eliminará de la base de datos.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📜 Generales e Investigación**")
            v_voto = st.checkbox("Saber Voto", value=bool(fila_datos.get("Voto")))
            v_ley = st.checkbox("Saber Ley", value=bool(fila_datos.get("Ley")))
            v_blanco = st.checkbox("Saber Blanco", value=bool(fila_datos.get("Blanco")))
            v_lema = st.checkbox("Saber Lema", value=bool(fila_datos.get("Lema")))
            v_camino = st.checkbox("Leer 'El Camino a Cristo'", value=bool(fila_datos.get("El Camino a Cristo")))
            v_genesis = st.checkbox("Lectura Génesis", value=bool(fila_datos.get("Génesis")))
            
        with col2:
            st.markdown("**🏕️ Arte de Acampar**")
            v_nudos = st.checkbox("Nudos Básicos", value=bool(fila_datos.get("Nudos Básicos")))
            v_pernoctar = st.checkbox("Pernoctar en Campamento", value=bool(fila_datos.get("Pernoctar Campamento")))
            v_carpa = st.checkbox("Saber armar Carpa", value=bool(fila_datos.get("Armar Carpa")))
            v_senales = st.checkbox("Señales de Pista", value=bool(fila_datos.get("Señales de Pista")))
            
        with col3:
            st.markdown("**🍎 Salud y Naturaleza**")
            v_temperancia = st.checkbox("Temperancia de Daniel", value=bool(fila_datos.get("Temperancia de Daniel")))
            v_menu = st.checkbox("Menú Vegetariano", value=bool(fila_datos.get("Menú Vegetariano")))
            v_natura = st.checkbox("Especialidad Naturaleza", value=bool(fila_datos.get("Especialidad Naturaleza")))
            v_ayuda = st.checkbox("2 Horas Ayuda Comunitaria", value=bool(fila_datos.get("2 Horas Ayuda Comunitaria")))

        if st.button("💾 SINCRONIZAR CAMBIOS"):
            fila_idx = df_base[df_base['Integrantes'] == conquistador].index[0] + 3
            hoy = datetime.now().strftime("%d/%m/%Y")
            
            # Diccionario de estado actual de los checkboxes
            estado_actual = {
                "Voto": v_voto, "Ley": v_ley, "Blanco": v_blanco, "Lema": v_lema,
                "El Camino a Cristo": v_camino, "Génesis": v_genesis,
                "Nudos Básicos": v_nudos, "Pernoctar Campamento": v_pernoctar,
                "Armar Carpa": v_carpa, "Señales de Pista": v_senales,
                "Temperancia de Daniel": v_temperancia, "Menú Vegetariano": v_menu,
                "Especialidad Naturaleza": v_natura, "2 Horas Ayuda Comunitaria": v_ayuda
            }
            
            # Lógica de actualización o limpieza
            for req, esta_marcado in estado_actual.items():
                if req in headers:
                    col_idx = headers.index(req) + 1
                    # Si se marca, ponemos la fecha. Si se desmarca, ponemos vacío ""
                    valor_celda = hoy if esta_marcado else ""
                    sheet.update_cell(fila_idx, col_idx, valor_celda)
            
            # Actualizar fecha de control general (Columna B)
            sheet.update_cell(fila_idx, 2, hoy)
            
            st.success(f"¡Base de datos sincronizada para {conquistador}!")
            st.rerun()
else:
    st.warning("Configurando conexión...")
