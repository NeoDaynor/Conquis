import base64
import json
import os

import streamlit as st


def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as file:
            data = file.read()
        return base64.b64encode(data).decode()
    except OSError:
        return ""


def load_users():
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r", encoding="utf-8") as file:
                return json.load(file).get("users", [])
        except (json.JSONDecodeError, OSError):
            return []
    return []


def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["usuario"] == username and user["password"] == password:
            if "rol" not in user:
                user["rol"] = "conqui"
            return user
    return None


def mostrar_login():
    st.markdown(
        """
        <style>
        .login-shell {
            max-width: 640px;
            margin: 0 auto;
            padding-top: 0.6rem;
        }
        .login-shell [data-testid="stForm"] {
            margin-top: 0.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("### Iniciar sesion")
        user_input = st.text_input("Usuario", placeholder="Escriba su usuario")
        pass_input = st.text_input("Contrasena", type="password", placeholder="Escriba su contrasena")

        if st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True):
            user_data = authenticate(user_input, pass_input)

            if user_data:
                st.session_state["authenticated"] = True
                st.session_state["user_info"] = user_data
                st.success(f"Bienvenido {user_data['nombre']} ({user_data['rol']})")
                st.rerun()
            else:
                st.error("Credenciales no validas. Reintente.")
    st.markdown("</div>", unsafe_allow_html=True)
