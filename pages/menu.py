import streamlit as st
import base64

st.set_page_config(page_title="Menú - Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

user = st.session_state.get("user_info", {"nombre": "Usuario"})
bin_pc = get_base64('images/fondopc.jpg')
bin_mob = get_base64('images/fondocelu.webp')

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    :root {{
        --bg-card: rgba(255, 255, 255, 0.9);
        --text-color: #1E293B;
    }}
    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-card: rgba(30, 41, 59, 0.9);
            --text-color: #F1F5F9;
        }}
    }}
    .stApp {{
        background-attachment: fixed; background-size: cover; background-position: center;
    }}
    @media (min-width: 769px) {{ .stApp {{ background-image: url("data:image/jpg;base64,{bin_pc}"); }} }}
    @media (max-width: 768px) {{ .stApp {{ background-image: url("data:image/webp;base64,{bin_mob}"); }} }}
    
    .welcome-card {{
        background-color: var(--bg-card); padding: 30px; border-radius: 20px;
        border: 1px solid #0070C0; text-align: center; color: var(--text-color);
    }}
    div.stButton > button {{
        background-color: white !important; color: #0070C0 !important;
        border: 2px solid #0070C0 !important; border-radius: 15px !important;
        height: 120px !important; width: 100% !important; font-weight: bold !important;
    }}
    div.stButton > button:hover {{
        background-color: #0070C0 !important; color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px #000;'>CLUB LAKONN</h1>", unsafe_allow_html=True)

_, col_center, _ = st.columns([1, 2, 1])
with col_center:
    st.markdown(f'<div class="welcome-card"><h2>Bienvenido, {user["nombre"]}</h2><p>Selecciona unidad:</p></div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🪐\n\nORION"):
            st.session_state["unidad_seleccionada"] = "Orion"
            st.switch_page("pages/amigo.py")
    with c2:
        if st.button("🐆\n\nPUMAS"):
            st.session_state["unidad_seleccionada"] = "Pumas"
            st.switch_page("pages/amigo.py")
    with c3:
        if st.button("🎖️\n\nLIDERES"):
            st.session_state["unidad_seleccionada"] = "Lideres"
            st.switch_page("pages/amigo.py")

with st.sidebar:
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.switch_page("app.py")
