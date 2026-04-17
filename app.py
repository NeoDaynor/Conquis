import streamlit as st
import json
import os
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Club Lakonn - Acceso", layout="wide")

# --- CSS PARA FONDOS ADAPTATIVOS Y OCULTAR MENÚS ---
st.markdown(
    """
    <style>
    /* Ocultar menús de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    button[title="Manage app"] {display: none;}

    /* Configuración de Fondo base */
    .stApp {
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }

    /* FONDO PARA PC (Pantallas mayores a 768px) */
    @media (min-width: 769px) {
        .stApp {
            background-image: url("https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/images/fondopc.jpg");
        }
    }

    /* FONDO PARA CELULAR (Pantallas menores o iguales a 768px) */
    @media (max-width: 768px) {
        .stApp {
            background-image: url("https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/images/fondocelu.webp");
        }
    }

    /* Estilo para la tarjeta de login para que resalte sobre el fondo */
    .login-card {
        text-align: center; 
        background-color: rgba(240, 242, 246, 0.9); 
        padding: 30px; 
        border-radius: 15px; 
        border: 1px solid #0070C0;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- NOTA IMPORTANTE ---
# Para que las imágenes carguen correctamente en Streamlit Cloud desde CSS, 
# se recomienda usar la URL directa de GitHub (raw) o servirlas localmente.
# Si prefieres local, asegúrate de que las rutas 'images/fondopc.jpg' 
# y 'images/fondocelu.webp' existan en tu repo.

# --- FUNCIONES DE AUTENTICACIÓN ---
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

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "unidad_seleccionada" not in st.session_state:
    st.session_state["unidad_seleccionada"] = None

# --- ENCABEZADO CON LOGO ---
col_t1, col_t2 = st.columns([8, 1])
with col_t2:
    try:
        logo = Image.open("images/LogoLakonn.png")
        st.image(logo, use_container_width=True)
    except Exception:
        pass

# --- PANTALLA DE LOGEO ---
if not st.session_state["authenticated"]:
    _, center_col, _ = st.columns([1, 1.5, 1])
    
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="login-card">
                <h1 style='color: #0070C0; margin-bottom: 0;'>BIENVENIDO</h1>
                <p style='color: #555;'>Gestión de Conquistadores - Club Lakonn</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            user_input = st.text_input("Usuario", placeholder="Ingrese su usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
            
            if submit:
                user_data = authenticate(user_input, pass_input)
                if user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_data
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

# --- PANTALLA DE SELECCIÓN ---
else:
    user = st.session_state["user_info"]
    st.sidebar.markdown(f"### 👤 {user['nombre']}")
    st.sidebar.info(f"**Cargo:** {user['cargo']}")
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #0070C0;'>CLUB LAKONN</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"<h4 style='text-align: center;'>Hola {user['nombre']}, selecciona una unidad:</h4>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        unidades = [
            {"nombre": "🪐 UNIDAD ORION", "id": "Orion"},
            {"nombre": "🐆 UNIDAD PUMAS", "id": "Pumas"},
            {"nombre": "🎖️ UNIDAD LIDERES", "id": "Lideres"}
        ]
        for u in unidades:
            if st.button(u["nombre"], key=u["id"], use_container_width=True, type="secondary"):
                st.session_state["unidad_seleccionada"] = u["id"]
                st.switch_page("pages/gestion.py")
