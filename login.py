import streamlit as st
import json
import os
import base64
from PIL import Image

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)['users']
    return []

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['usuario'] == username and user['password'] == password:
            return user
    return None

def mostrar_login():
    # Estilos CSS idénticos (Colores y Fondos)
    bin_str_pc = get_base64_of_bin_file('images/fondopc.jpg')
    bin_str_mob = get_base64_of_bin_file('images/fondocelu.webp')
    
    st.markdown(
        f"""
        <style>
        #MainMenu, footer, header, .stAppDeployButton {{visibility: hidden;}}
        .stApp {{
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_str_pc}"); }} }}
        @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_str_mob}"); }} }}

        [data-testid="stForm"], .login-header {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid #0070C0 !important;
            padding: 30px !important;
            box-shadow: 0px 8px 25px rgba(0,0,0,0.4);
        }}
        .login-header {{ border-radius: 20px 20px 0 0 !important; border-bottom: none !important; text-align: center; margin-top: 30px; }}
        [data-testid="stForm"] {{ border-radius: 0 0 20px 20px !important; margin-top: -1px; }}
        .stMarkdown p, label, h1, h3 {{ color: #1E1E1E !important; }}
        button[kind="primaryFormSubmit"] {{ background-color: #0e1117 !important; color: white !important; border: 1px solid #0070C0 !important; }}
        </style>
        """, 
        unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.markdown('<div class="login-header"><h1 style="color: #0070C0;">BIENVENIDO</h1><p>Gestión de Conquistadores - Club Lakonn</p></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            user_input = st.text_input("Usuario", placeholder="Escriba su usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Escriba su contraseña")
            if st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True):
                user_data = authenticate(user_input, pass_input)
                if user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_data
                    st.rerun()
                else:
                    st.error("Credenciales no válidas.")
