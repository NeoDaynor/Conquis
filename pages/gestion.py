import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- SEGURIDAD DE NAVEGACIÓN ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]

# --- FUNCIÓN DE ESTILO (CORRECCIÓN image_f4a2d0.png) ---
def estilo_azul(val):
    if val and str(val).strip() != "":
        return 'background-color: #0070C0; color: #0070C0;'
    return ''

# --- CONEXIÓN A DATOS ---
def get_client():
    creds = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

client = get_client()
sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- LECTURA Y FILTRADO ---
raw_data = sheet.get_all_values()
headers = raw_data[1]  # Encabezados en fila 2
df_full = pd.DataFrame(raw_data[2:], columns=headers)

# Filtramos solo los integrantes de la unidad elegida (image_f60f4c.png)
df_unidad = df_full[df_full['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---
st.title(f"🛡️ Unidad: {unidad_actual.upper()}")
if st.button("⬅️ Cambiar Unidad"):
    st.switch_page("app.py")

st.divider()

# --- CUADRO DE CUMPLIMIENTO (CORRECCIÓN applymap -> map) ---
st.subheader("📊 Avance de la Unidad")
# SOLUCIÓN AL ERROR DE image_f4a2d0.png: Usamos .map() en lugar de .applymap()
st.dataframe(
    df_unidad.style.map(estilo_azul, subset=df_unidad.columns[2:]),
    use_container_width=True,
    hide_index=True
)

# --- GESTIÓN DE INTEGRANTES (image_f603c7.png) ---
with st.expander(f"📝 Registrar Avances de {unidad_actual}", expanded=True):
    nombres = df_unidad['Integrantes'].tolist()
    
    if not nombres:
        st.warning(f"No hay integrantes registrados para {unidad_actual}.")
    else:
        conquistador = st.selectbox("Seleccione Integrante:", nombres)
        fila_data = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        # Columnas de requisitos
        c1, c2, c3 = st.columns(3)
        nuevo_estado = {}
        requisitos = [
            "Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
            "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
            "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"
        ]

        for i, r in enumerate(requisitos):
            col = c1 if i < 6 else (c2 if i < 10 else c3)
            esta_marcado = bool(fila_data.get(r))
            val = col.checkbox(r, value=esta_marcado, key=f"ch_{r}")
            nuevo_estado[r] = val
            
            # Alerta visual al desmarcar (image_f596ea.png)
            if esta_marcado and not val:
                col.caption(f"⚠️ Se eliminará: {r}")

        # --- GUARDADO ---
        borrados = [r for r, v in nuevo_estado.items() if bool(fila_data.get(r)) and not v]
        confirmar = st.toggle("Confirmar borrado de datos", key="conf") if borrados else True

        if st.button("💾 ACTUALIZAR GOOGLE SHEETS", type="primary"):
            if borrados and not confirmar:
                st.error("Por favor, confirma la eliminación de requisitos.")
            else:
                idx_excel = df_full[df_full['Integrantes'] == conquistador].index[0] + 3
                hoy = datetime.now().strftime("%d/%m/%Y")
                
                with st.status("Sincronizando...") as s:
                    for req, check in nuevo_estado.items():
                        c_idx = headers.index(req) + 1
                        sheet.update_cell(idx_excel, c_idx, hoy if check else "")
                    
                    sheet.update_cell(idx_excel, headers.index("Ult. Actualizacion") + 1, hoy)
                    s.update(label="Sincronización Exitosa", state="complete")
                st.rerun()
