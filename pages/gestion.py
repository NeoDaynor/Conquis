import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- 1. VERIFICACIÓN DE SEGURIDAD ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.warning("⚠️ No has seleccionado una unidad. Volviendo al inicio...")
    st.stop()

unidad = st.session_state["unidad_seleccionada"]

# --- 2. CONEXIÓN A INFRAESTRUCTURA GCP ---
def get_gspread_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

client = get_gspread_client()
if client:
    sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- 3. PROCESAMIENTO Y FILTRADO (image_f60f4c.png) ---
if client:
    data = sheet.get_all_values()
    headers = data[1] # Fila 2
    df_completo = pd.DataFrame(data[2:], columns=headers)

    # FILTRO CRÍTICO: Solo integrantes de la unidad seleccionada
    df_base = df_completo[df_completo['Unidad'] == unidad].copy()

    # --- 4. INTERFAZ ---
    st.title(f"🛡️ Gestión: Unidad {unidad.upper()}")
    
    if st.button("⬅️ Volver al Inicio"):
        st.switch_page("app.py")

    # Dashboard filtrado
    st.markdown("### 📊 Cumplimiento de la Unidad")
    # (Lógica de heatmap azul omitida por brevedad, se mantiene igual a la anterior)
    st.dataframe(df_base[['Integrantes', 'Ult. Actualizacion']], use_container_width=True, hide_index=True)

    st.divider()

    # --- 5. REGISTRO DE AVANCES FILTRADO ---
    with st.expander(f"📝 Registrar Avances - {unidad}", expanded=True):
        # El selectbox ahora solo muestra los nombres de esa unidad
        lista_integrantes = df_base['Integrantes'].tolist()
        
        if not lista_integrantes:
            st.error(f"No hay integrantes registrados para la unidad {unidad}")
        else:
            conquistador = st.selectbox("Seleccione al Conquistador:", lista_integrantes)
            fila_datos = df_base[df_base['Integrantes'] == conquistador].iloc[0]
            
            # (Aquí va el resto de tu lógica de checkboxes y sincronización...)
            # Asegúrate de usar la lógica de desmarcado con el caption ⚠️ que implementamos antes
            
            col1, col2, col3 = st.columns(3)
            # ... renderizado de requisitos ...

            if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
                # IMPORTANTE: Para buscar la fila real en el Excel original
                # Buscamos el índice en el df_completo para que coincida con la fila del Sheet
                fila_idx = df_completo[df_completo['Integrantes'] == conquistador].index[0] + 3
                
                # Ejecutar sincronización (Misma lógica anterior)
                st.success(f"¡Sincronizado con éxito en {unidad}!")
                st.rerun()
