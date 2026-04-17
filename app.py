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
    headers = data[1]  # Fila 2
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

    # --- 6. SISTEMA DE ACTUALIZACIÓN CON ALERTA INMEDIATA ---
    with st.expander("📝 Registrar o Corregir Avances"):
        conquistador = st.selectbox("Seleccione al Conquistador:", df_base['Integrantes'].tolist())
        
        # Obtener datos actuales de la DB
        fila_datos = df_base[df_base['Integrantes'] == conquistador].iloc[0]
        
        # Contenedor para el Pop-up de advertencia
        aviso_placeholder = st.empty()
        
        col1, col2, col3 = st.columns(3)
        
        # Diccionario para capturar el nuevo estado
        estado_nuevo = {}

        with col1:
            st.markdown("**📜 Generales e Investigación**")
            # Lista de requisitos para esta columna
            reqs1 = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis"]
            for r in reqs1:
                estado_nuevo[r] = st.checkbox(r, value=bool(fila_datos.get(r)), key=f"cb_{r}")
            
        with col2:
            st.markdown("**🏕️ Arte de Acampar**")
            reqs2 = ["Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista"]
            for r in reqs2:
                estado_nuevo[r] = st.checkbox(r, value=bool(fila_datos.get(r)), key=f"cb_{r}")
            
        with col3:
            st.markdown("**🍎 Salud y Naturaleza**")
            reqs3 = ["Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]
            for r in reqs3:
                estado_nuevo[r] = st.checkbox(r, value=bool(fila_datos.get(r)), key=f"cb_{r}")

        # --- LÓGICA DE ALERTA INSTANTÁNEA ---
        desmarcados = [r for r, val in estado_nuevo.items() if bool(fila_datos.get(r)) and not val]
        
        confirmacion_final = True # Por defecto es True si no hay desmarcados
        
        if desmarcados:
            with aviso_placeholder.container():
                st.error(f"🚨 **CUIDADO:** Has desmarcado: {', '.join(desmarcados)}. Esto eliminará el registro de la base de datos.")
                confirmacion_final = st.toggle("Confirmar eliminación de estos requisitos", value=False)

        # --- BOTÓN DE GUARDADO ---
        if st.button("💾 SINCRONIZAR CAMBIOS"):
            if not confirmacion_final:
                st.warning("Debes activar el interruptor de confirmación para poder borrar registros.")
            else:
                fila_idx = df_base[df_base['Integrantes'] == conquistador].index[0] + 3
                hoy = datetime.now().strftime("%d/%m/%Y")
                
                with st.status("Sincronizando con Google Sheets...", expanded=True) as status:
                    for req, esta_marcado in estado_nuevo.items():
                        if req in headers:
                            col_idx = headers.index(req) + 1
                            valor_celda = hoy if esta_marcado else ""
                            # Solo actualizamos si el valor cambió para ahorrar cuota de API
                            if str(fila_datos.get(req)) != valor_celda:
                                sheet.update_cell(fila_idx, col_idx, valor_celda)
                    
                    sheet.update_cell(fila_idx, 2, hoy)
                    status.update(label="✅ Sincronización completada", state="complete", expanded=False)
                
                st.success(f"¡Base de datos actualizada para {conquistador}!")
                st.rerun()
else:
    st.warning("Configurando conexión...")
