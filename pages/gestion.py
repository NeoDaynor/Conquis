import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- SEGURIDAD ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]

# --- INFRAESTRUCTURA DE DATOS ---
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
    data = sheet.get_all_values()
    headers = data[1] # Fila de títulos
    df_completo = pd.DataFrame(data[2:], columns=headers)
    
    # FILTRO: Solo integrantes de la unidad (image_f60f4c.png)
    df_unidad = df_completo[df_completo['Unidad'] == unidad_actual].copy()

    # --- INTERFAZ ---
    st.title(f"🛡️ Gestión: {unidad_actual.upper()}")
    if st.button("⬅️ Cambiar Unidad"):
        st.switch_page("app.py")

    st.divider()

    # REGISTRO DE AVANCES (image_f603c7.png)
    with st.expander(f"📝 Integrantes de {unidad_actual}", expanded=True):
        nombres = df_unidad['Integrantes'].tolist()
        
        if not nombres:
            st.warning("No se encontraron integrantes en esta unidad.")
        else:
            conquistador = st.selectbox("Seleccione:", nombres)
            fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            estado_nuevo = {}
            
            # Listado de requisitos para el formulario
            requisitos = [
                "Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"
            ]

            for i, r in enumerate(requisitos):
                t_col = col1 if i < 6 else (col2 if i < 10 else col3)
                valor_actual = bool(fila_persona.get(r))
                
                # Checkbox con alerta integrada para celular (image_f596ea.png)
                marcado = t_col.checkbox(r, value=valor_actual, key=f"ch_{r}")
                estado_nuevo[r] = marcado
                
                if valor_actual and not marcado:
                    t_col.caption(f"⚠️ **Atención: Se borrará {r}**")

            # --- SINCRONIZACIÓN ---
            desmarcados = [r for r, v in estado_nuevo.items() if bool(fila_persona.get(r)) and not v]
            confirmar = st.toggle("Confirmar cambios de eliminación", key="conf") if desmarcados else True

            if st.button("💾 SINCRONIZAR CAMBIOS", type="primary"):
                if desmarcados and not confirmar:
                    st.error("Debes confirmar la eliminación de datos.")
                else:
                    # Buscamos la fila real en el sheet
                    idx_excel = df_completo[df_completo['Integrantes'] == conquistador].index[0] + 3
                    hoy = datetime.now().strftime("%d/%m/%Y")
                    
                    with st.status("Actualizando Google Sheets...") as s:
                        for req, es_marcado in estado_nuevo.items():
                            col_pos = headers.index(req) + 1
                            val = hoy if es_marcado else ""
                            if str(fila_persona.get(req)) != val:
                                sheet.update_cell(idx_excel, col_pos, val)
                        
                        sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                        s.update(label="Sincronización completa", state="complete")
                    st.rerun()
