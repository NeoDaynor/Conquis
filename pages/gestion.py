import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- BLOQUEO DE SEGURIDAD ---
if "unidad_seleccionada" not in st.session_state or st.session_state["unidad_seleccionada"] is None:
    st.switch_page("app.py")

unidad_actual = st.session_state["unidad_seleccionada"]

# --- CONEXIÓN ---
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

client = get_gspread_client()
sheet = client.open("RequisitosConquistadores").worksheet("Amigo")

# --- CARGA Y FILTRADO DE DATOS ---
data = sheet.get_all_values()
headers = data[1]  # Encabezados en fila 2
df_completo = pd.DataFrame(data[2:], columns=headers)

# Filtrar por unidad seleccionada (image_f60f4c.png)
df_unidad = df_completo[df_completo['Unidad'] == unidad_actual].copy()

# --- INTERFAZ ---
st.title(f"🛡️ Unidad: {unidad_actual.upper()}")
if st.button("⬅️ Cambiar Unidad"):
    st.switch_page("app.py")

st.divider()

# --- REGISTRO DE AVANCES ---
with st.expander(f"📝 Registrar Avances de {unidad_actual}", expanded=True):
    lista_nombres = df_unidad['Integrantes'].tolist()
    
    if not lista_nombres:
        st.warning(f"No hay integrantes en la unidad {unidad_actual}. Verifica el Excel.")
    else:
        conquistador = st.selectbox("Seleccione Integrante:", lista_nombres)
        fila_datos = df_unidad[df_unidad['Integrantes'] == conquistador].iloc[0]
        
        # Lógica de requisitos (Columnas)
        col1, col2, col3 = st.columns(3)
        estado_nuevo = {}
        
        requisitos = [
            "Voto", "Ley", "Blanco", "Lema", "El Camino a Cristo", "Génesis",
            "Nudos Básicos", "Pernoctar Campamento", "Armar Carpa", "Señales de Pista",
            "Temperancia de Daniel", "Menú Vegetariano", "Especialidad Naturaleza", "2 Horas Ayuda Comunitaria"
        ]

        for i, r in enumerate(requisitos):
            target_col = col1 if i < 6 else (col2 if i < 10 else col3)
            estaba_marcado = bool(fila_datos.get(r))
            
            # Checkbox con alerta inmediata (Mejora anterior)
            val = target_col.checkbox(r, value=estaba_marcado, key=f"ch_{r}")
            estado_nuevo[r] = val
            if estaba_marcado and not val:
                target_col.caption(f"⚠️ Se borrará: {r}")

        # Validación de desmarcados
        desmarcados = [r for r, v in estado_nuevo.items() if bool(fila_datos.get(r)) and not v]
        
        confirmar = True
        if desmarcados:
            st.info("Hay cambios que implican borrar registros.")
            confirmar = st.toggle("Confirmar borrado de avances", key="confirm_delete")

        # Botón Sincronizar
        if st.button("💾 ACTUALIZAR EN GOOGLE SHEETS", type="primary"):
            if desmarcados and not confirmar:
                st.error("Confirma la eliminación antes de guardar.")
            else:
                # Buscamos la fila original en el df_completo para el update
                idx_real = df_completo[df_completo['Integrantes'] == conquistador].index[0] + 3
                hoy = datetime.now().strftime("%d/%m/%Y")
                
                for req, marcado in estado_nuevo.items():
                    col_idx = headers.index(req) + 1
                    nuevo_valor = hoy if marcado else ""
                    if str(fila_datos.get(req)) != nuevo_valor:
                        sheet.update_cell(idx_real, col_idx, nuevo_valor)
                
                sheet.update_cell(idx_real, headers.index("Ult. Actualizacion") + 1, hoy)
                st.success(f"Datos de {conquistador} actualizados.")
                st.rerun()
