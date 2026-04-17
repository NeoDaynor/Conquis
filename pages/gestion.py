import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- BLOQUEO DE NAVEGACIÓN ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]

# --- CONEXIÓN A GOOGLE SHEETS ---
def get_gspread_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de infraestructura: {e}")
        return None

client = get_gspread_client()

if client:
    sheet = client.open("RequisitosConquistadores").worksheet("Amigo")
    data = sheet.get_all_values()
    headers = data[1] # Fila de encabezados
    df_completo = pd.DataFrame(data[2:], columns=headers)
    
    # FILTRADO DINÁMICO POR UNIDAD
    df_unidad = df_completo[df_completo['Unidad'] == unidad_actual].copy()

    # --- INTERFAZ ---
    st.title(f"🛡️ Gestión: {unidad_actual.upper()}")
    if st.button("⬅️ Volver"):
        st.switch_page("app.py")

    st.divider()

    with st.expander(f"📝 Registrar Avances - {unidad_actual}", expanded=True):
        nombres = df_unidad['Integrantes'].tolist()
        
        if not nombres:
            st.warning(f"No hay integrantes en la unidad {unidad_actual}.")
        else:
            conquistador = st.selectbox("Seleccione Integrante:", nombres)
            fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            estado_nuevo = {}
            
            requisitos = [
                "Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"
            ]

            for i, r in enumerate(requisitos):
                t_col = col1 if i < 6 else (col2 if i < 10 else col3)
                checked_db = bool(fila_persona.get(r))
                
                # Checkbox con alerta debajo para móvil
                val = t_col.checkbox(r, value=checked_db, key=f"ch_{r}")
                estado_nuevo[r] = val
                
                if checked_db and not val:
                    t_col.caption(f"⚠️ **Se eliminará: {r}**")

            # --- LÓGICA DE ACTUALIZACIÓN ---
            borrados = [r for r, v in estado_nuevo.items() if bool(fila_persona.get(r)) and not v]
            
            confirmado = True
            if borrados:
                st.info("⚠️ Hay requisitos desmarcados.")
                confirmado = st.toggle("Confirmar eliminación", key="del_confirm")

            if st.button("💾 SINCRONIZAR", type="primary"):
                if borrados and not confirmado:
                    st.error("Confirma el borrado antes de guardar.")
                else:
                    # Buscamos la fila original en el Sheet (índice + 3)
                    idx_real = df_completo[df_completo['Integrantes'] == conquistador].index[0] + 3
                    hoy = datetime.now().strftime("%d/%m/%Y")
                    
                    with st.status("Sincronizando...") as s:
                        for req, marcado in estado_nuevo.items():
                            c_idx = headers.index(req) + 1
                            val_to_send = hoy if marcado else ""
                            if str(fila_persona.get(req)) != val_to_send:
                                sheet.update_cell(idx_real, c_idx, val_to_send)
                        
                        sheet.update_cell(idx_real, headers.index("Ult. Actualizacion") + 1, hoy)
                        s.update(label="Éxito", state="complete")
                    st.rerun()
