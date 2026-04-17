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

# --- 3. LÓGICA DE ESTILO ---
def estilo_heatmap(val):
    if val and str(val).strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# --- 4. PROCESAMIENTO DE DATOS ---
if client:
    # Cacheamos la data para que la interfaz no sea lenta al interactuar
    data = sheet.get_all_values()
    headers = data[1]
    df_base = pd.DataFrame(data[2:], columns=headers)

    # MAPEO DASHBOARD
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

    # --- 5. INTERFAZ ---
    st.title("🛡️ Sistema de Gestión: Clase de Amigo")
    st.dataframe(
        df_dash.style.map(estilo_heatmap, subset=df_dash.columns[2:]),
        use_container_width=True, hide_index=True
    )

    st.divider()

    # --- 6. SISTEMA DE ACTUALIZACIÓN CON POP-UP DE SEGURIDAD ---
    with st.expander("📝 Registrar o Corregir Avances", expanded=True):
        conquistador = st.selectbox("Seleccione al Conquistador:", df_base['Integrantes'].tolist())
        fila_datos = df_base[df_base['Integrantes'] == conquistador].iloc[0]
        
        # Columnas de Checkboxes
        col1, col2, col3 = st.columns(3)
        estado_nuevo = {}
        
        todos_los_requisitos = [
            "Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
            "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
            "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"
        ]

        # Renderizar Checks
        for i, r in enumerate(todos_los_requisitos):
            target_col = col1 if i < 6 else (col2 if i < 10 else col3)
            estado_nuevo[r] = target_col.checkbox(r, value=bool(fila_datos.get(r)), key=f"ch_{r}")

        # --- LÓGICA DE POP-UP (Inmediata) ---
        desmarcados = [r for r, val in estado_nuevo.items() if bool(fila_datos.get(r)) and not val]
        
        if desmarcados:
            # st.popover crea un botón que al abrirse actúa como una ventana emergente
            with st.popover("⚠️ ¡ATENCIÓN! REQUISITOS DESMARCADOS", use_container_width=True):
                st.error(f"Has desmarcado: {', '.join(desmarcados)}")
                st.write("Si guardas ahora, estos registros se borrarán permanentemente de Google Sheets.")
                confirmar = st.toggle("Confirmar eliminación", key="confirm_delete")
        else:
            confirmar = True

        # --- BOTÓN DE GUARDAR ---
        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary", use_container_width=True):
            if desmarcados and not st.session_state.get("confirm_delete", False):
                st.warning("⚠️ Acción bloqueada: Debes abrir el Pop-up rojo y confirmar la eliminación.")
            else:
                fila_idx = df_base[df_base['Integrantes'] == conquistador].index[0] + 3
                hoy = datetime.now().strftime("%d/%m/%Y")
                
                with st.status("Actualizando Base de Datos...") as s:
                    for req, valor in estado_nuevo.items():
                        if req in headers:
                            col_idx = headers.index(req) + 1
                            nuevo_val = hoy if valor else ""
                            if str(fila_datos.get(req)) != nuevo_val:
                                sheet.update_cell(fila_idx, col_idx, nuevo_val)
                    
                    sheet.update_cell(fila_idx, 2, hoy)
                    s.update(label="Sincronización Exitosa", state="complete")
                st.rerun()
else:
    st.warning("Configurando conexión...")
