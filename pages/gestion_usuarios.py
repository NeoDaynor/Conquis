import streamlit as st
import json
import os

# Configuración del archivo según tu estructura
DB_PATH = 'users.json'

def cargar_datos():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Estructura inicial si el archivo no existe
    return {"users": []}

def guardar_datos(datos):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def main():
    st.set_page_config(page_title="Administración de Usuarios", layout="wide")
    st.title("👤 Panel de Gestión de Usuarios")

    # Cargar datos en la sesión
    if 'data' not in st.session_state:
        st.session_state.data = cargar_datos()

    # --- FORMULARIO: CREAR NUEVO ---
    with st.expander("➕ Registrar Nuevo Miembro"):
        with st.form("nuevo_usuario_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                nombre = st.text_input("Nombre Completo")
                cargo = st.text_input("Cargo")
                correo = st.text_input("Correo")
            with col_b:
                usuario = st.text_input("Nombre de Usuario (Login)")
                password = st.text_input("Contraseña", type="password")
                rol = st.selectbox("Rol de Sistema", ["admin", "user"])
            
            submit = st.form_submit_button("Guardar en JSON")

            if submit:
                # Generar ID correlativo
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
                st.success(f"Usuario {usuario} añadido correctamente.")
                st.rerun()

    # --- TABLA DE EDICIÓN Y ELIMINACIÓN ---
    st.subheader("Listado de Usuarios Activos")
    
    # Encabezados de columna
    h1, h2, h3, h4, h5, h6 = st.columns([0.5, 2, 1.5, 1.5, 1, 0.5])
    h1.write("**ID**")
    h2.write("**Nombre**")
    h3.write("**Cargo**")
    h4.write("**Usuario**")
    h5.write("**Rol**")
    h6.write("**Acción**")

    # Iterar sobre la lista de usuarios (usamos una copia para evitar errores al eliminar)
    for i, user in enumerate(st.session_state.data['users']):
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 2, 1.5, 1.5, 1, 0.5])
        
        with c1:
            st.write(user['id'])
        with c2:
            nuevo_nombre = st.text_input("Nom", user['nombre'], key=f"n_{i}", label_visibility="collapsed")
        with c3:
            nuevo_cargo = st.text_input("Car", user['cargo'], key=f"c_{i}", label_visibility="collapsed")
        with c4:
            nuevo_user_login = st.text_input("Usu", user['usuario'], key=f"u_{i}", label_visibility="collapsed")
        with c5:
            nuevo_rol = st.selectbox("Rol", ["admin", "user"], index=0 if user['rol'] == "admin" else 1, key=f"r_{i}", label_visibility="collapsed")
        with c6:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.data['users'].pop(i)
                guardar_datos(st.session_state.data)
                st.rerun()

        # Detección de cambios automática
        if (nuevo_nombre != user['nombre'] or nuevo_cargo != user['cargo'] or 
            nuevo_user_login != user['usuario'] or nuevo_rol != user['rol']):
            
            st.session_state.data['users'][i].update({
                "nombre": nuevo_nombre,
                "cargo": nuevo_cargo,
                "usuario": nuevo_user_login,
                "rol": nuevo_rol
            })
            guardar_datos(st.session_state.data)
            st.toast("Cambios guardados")

if __name__ == "__main__":
    main()
