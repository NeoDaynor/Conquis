import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- SEGURIDAD ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]

# --- FUNCIÓN DE ESTILO (SOLUCIÓN AL ERROR image_f4a2d0.png) ---
def estilo_azul(val):
    if val and val.strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# --- CONEXIÓN ---
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

client = get_gspread_client()
sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- PROCESAMIENTO ---
data = sheet.get_all_values()
headers = data[1]
df_completo = pd.DataFrame(data[2:], columns=headers)

# Filtro por Unidad (image_f60f4c.png)
df_unidad = df_completo[df_completo['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---
st.title(f"🛡️ Gestión: {unidad_actual.upper()}")
if st.button("⬅️ Volver"):
    st.switch_page("app.py")

st.divider()

# TABLA DE CUMPLIMIENTO CORREGIDA (Línea 53 corregida de image_f4a2d0.png)
st.markdown("### 📊 Cuadro de Cumplimiento")
# Usamos .map() en lugar de .applymap() para compatibilidad con Pandas 2.0+
st.dataframe(
    df_unidad.style.map(estilo_azul, subset=df_unidad.columns[2:]), 
    use_container_width=True, 
    hide_index=True
)

# --- REGISTRO (image_f603c7.png) ---
with st.expander(f"📝 Registro de {unidad_actual}", expanded=True):
    nombres = df_unidad['Integrantes'].tolist()
    if nombres:
        conquistador = st.selectbox("Seleccione:", nombres)
        fila_persona = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        estado_nuevo = {}
        requisitos = ["Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
                      "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
                      "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"]

        for i, r in enumerate(requisitos):
            t_col = col1 if i < 6 else (col2 if i < 10 else col3)
            marcado_db = bool(fila_persona.get(r))
            val = t_col.checkbox(r, value=marcado_db, key=f"ch_{r}")
            estado_nuevo[r] = val
            if marcado_db and not val:
                t_col.caption(f"⚠️ Se borrará: {r}")

        # --- SINCRONIZACIÓN ---
        desmarcados = [r for r, v in estado_nuevo.items() if bool(fila_persona.get(r)) and not v]
        confirmar = st.toggle("Confirmar eliminación", key="c") if desmarcados else True

        if st.button("💾 SINCRONIZAR", type="primary"):
            if desmarcados and not confirmar:
                st.error("Confirma el borrado antes de guardar.")
            else:
                idx_real = df_completo[df_completo['Integrantes'] == conquistador].index[0] + 3
                hoy = datetime.now().strftime("%d/%m/%Y")
                for req, marcado in estado_nuevo.items():
                    c_idx = headers.index(req) + 1
                    sheet.update_cell(idx_real, c_idx, hoy if marcado else "")
                sheet.update_cell(idx_real, headers.index("Ult. Actualizacion") + 1, hoy)
                st.success("Sincronizado.")
                st.rerun()
