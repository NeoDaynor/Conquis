import streamlit as st
import json
import os

# Al estar dentro de la carpeta /pages, Streamlit busca el JSON en la raíz del proyecto
DB_PATH = 'users.json'

def cargar_datos():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": []}

def guardar_datos(datos):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def main():
    st.set_page_config(page_title="Gestión de Usuarios", layout="wide")
    st.title("👤 Administración de Usuarios (JSON)")

    # Inicializar datos en la sesión
    if 'data' not in st.session_state:
        st.session_state.data = cargar_datos()

    # --- FORMULARIO: CREAR NUEVO ---
    with st.expander("➕ Registrar Nuevo Miembro"):
        with st.form("nuevo_usuario_form", clear_on_submit=True):
            c_a, c_b = st.columns(2)
            with c_a:
                nombre = st.text_input("Nombre Completo")
                cargo = st.text_input("Cargo")
                correo = st.text_input("Correo")
            with c_b:
                usuario = st.text_input("Nombre de Usuario")
                password = st.text_input("Contraseña", type="password")
                rol = st.selectbox("Rol", ["admin", "user"])
            
            submit = st.form_submit_button("Guardar Usuario")

            if submit:
                ids = [u['id'] for u in st.session_state.data['users']]
                nuevo_id = max(ids, default=0) + 1
                
                nuevo_user = {
                    "id": nuevo_id,
                    "nombre": nombre,
                    "cargo": cargo,
                    "correo": correo,
                    "rol": rol,
                    "usuario": usuario,
                    "password": password
                }
                
                st.session_state.data['users'].append(nuevo_user)
                guardar_datos(st.session_state.data)
                st.success(f"Usuario {usuario} guardado.")
                st.rerun()

    st.divider()

    # --- LISTADO DE EDICIÓN ---
    st.subheader("Usuarios actuales")
    
    for i, user in enumerate(st.session_state.data['users']):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 0.5])
            
            # Inputs con los datos actuales
            nuevo_nom = col1.text_input(f"Nombre", user['nombre'], key=f"n_{i}")
            nuevo_car = col2.text_input(f"Cargo", user['cargo'], key=f"c_{i}")
            nuevo_usu = col3.text_input(f"User", user['usuario'], key=f"u_{i}")
            nuevo_rol = col4.selectbox(f"Rol", ["admin", "user"], index=0 if user['rol']=="admin" else 1, key=f"r_{i}")
            
            if col5.button("🗑️", key=f"del_{i}"):
                st.session_state.data['users'].pop(i)
                guardar_datos(st.session_state.data)
                st.rerun()

            # Guardar si hubo cambios en los inputs
            if (nuevo_nom != user['nombre'] or nuevo_car != user['cargo'] or 
                nuevo_usu != user['usuario'] or nuevo_rol != user['rol']):
                
                st.session_state.data['users'][i].update({
                    "nombre": nuevo_nom,
                    "cargo": nuevo_car,
                    "usuario": nuevo_usu,
                    "rol": nuevo_rol
                })
                guardar_datos(st.session_state.data)
                st.toast("Actualizado")

if __name__ == "__main__":
    main()
