import streamlit as st
import json
import os
import base64

# --- 1. FUNCIONES AUXILIARES (Protocolo Base64) ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)['users']
    return []

def authenticate(username, password):
    users = load_users()
    for user in users:
        # Verificamos credenciales
        if user['usuario'] == username and user['password'] == password:
            # Aseguramos que el rol exista, si no, por defecto es conqui
            if "rol" not in user:
                user["rol"] = "conqui"
            return user
    return None

# --- 2. INTERFAZ DE LOGIN ---
def mostrar_login():
    # Estilos CSS (Mantenemos tu diseño original "Nada se elimina")
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
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #0070C0 !important;
            padding: 30px !important;
            box-shadow: 0px 8px 25px rgba(0,0,0,0.4);
        }}
        .login-header {{ 
            border-radius: 20px 20px 0 0 !important; 
            border-bottom: none !important; 
            text-align: center; 
            margin-top: 30px; 
        }}
        [data-testid="stForm"] {{ 
            border-radius: 0 0 20px 20px !important; 
            margin-top: -1px; 
        }}
        
        .stMarkdown p, label, h1, h3 {{ color: #1E1E1E !important; font-weight: bold; }}
        
        /* Estilo del botón de ingreso */
        button[kind="primaryFormSubmit"] {{ 
            background-color: #0070C0 !important; 
            color: white !important; 
            border-radius: 10px !important;
            height: 50px !important;
            font-weight: bold !important;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 1.8, 1])
    
    with center_col:
        # Cabecera del Login
        st.markdown(
            '<div class="login-header"><h1 style="color: #0070C0; margin-bottom:0;">BIENVENIDO</h1>'
            '<p style="color: #555;">Club Lakonn - Gestión de Conquistadores</p></div>', 
            unsafe_allow_html=True
        )
        
        # Formulario de Login
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            user_input = st.text_input("Usuario", placeholder="Escriba su usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Escriba su contraseña")
            
            if st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True):
                user_data = authenticate(user_input, pass_input)
                
                if user_data:
                    # Guardamos TODO el diccionario del usuario, incluyendo el ROL
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_data
                    st.success(f"Bienvenido {user_data['nombre']} ({user_data['rol']})")
                    st.rerun()
                else:
                    st.error("Credenciales no válidas. Reintente.")
