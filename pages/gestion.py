import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- SEGURIDAD ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]

# --- ESTILO TABLA ---
def estilo_azul(val):
    if val and str(val).strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# --- CONEXIÓN ---
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

client = get_client()
sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- DATOS ---
raw_data = sheet.get_all_values()
headers = raw_data[1]
df_full = pd.DataFrame(raw_data[2:], columns=headers)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---
st.title(f"🛡️ Unidad: {unidad_actual.upper()}")
if st.button("⬅️ Cambiar Unidad"):
    st.switch_page("app.py")

st.divider()

# TABLA DE AVANCE
st.subheader("📊 Avance General")
st.dataframe(
    df_unidad.style.map(estilo_azul, subset=df_unidad.columns[3:]),
    use_container_width=True,
    hide_index=True
)

# REGISTRO Y CORRECCIÓN (Aquí se aplicó la corrección solicitada)
with st.expander(f"📝 Registrar o Corregir Avances", expanded=True):
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        # Selector de integrante
        conquistador = st.selectbox("Seleccione al Conquistador:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            
            # CORRECCIÓN: Verificar si tiene datos reales en la DB
            valor_db = fila_persona.get(r)
            esta_cumplido = bool(valor_db and str(valor_db).strip() != "")
            
            # CORRECCIÓN: Key dinámico para limpiar el check al cambiar de integrante
            val = col.checkbox(
                r, 
                value=esta_cumplido, 
                key=f"ch_{r}_{conquistador.replace(' ', '_')}"
            )
            nuevo_estado[r] = val
            
            # Aviso de eliminación
            if esta_cumplido and not val:
                col.caption(f"⚠️ Se eliminará: {r}")

        # --- SINCRONIZACIÓN ---
        desmarcados = [req for req, estado in nuevo_estado.items() if bool(fila_persona.get(req)) and not estado]
        confirmar = True
        if desmarcados:
            st.warning("⚠️ Hay requisitos marcados que vas a eliminar.")
            confirmar = st.toggle("Confirmar eliminación", key="toggle_del")

        if st.button("💾 SINCRONIZAR CAMBIOS", type="primary", use_container_width=True):
            if desmarcados and not confirmar:
                st.error("Debes confirmar la eliminación antes de sincronizar.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                hoy = datetime.now().strftime("%d/%m/%Y")
                
                with st.status("Actualizando Google Sheets...") as s:
                    for req, check in nuevo_estado.items():
                        c_idx = headers.index(req) + 1
                        val_actual = fila_persona.get(req)
                        
                        # Solo actualizamos si el estado cambió
                        if check and not bool(val_actual):
                            sheet.update_cell(idx_excel, c_idx, hoy)
                        elif not check and bool(val_actual):
                            sheet.update_cell(idx_excel, c_idx, "")
                            
                    sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                    s.update(label="¡Sincronización Exitosa!", state="complete")
                st.rerun()
