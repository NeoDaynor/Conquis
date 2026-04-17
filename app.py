import streamlit as st
import base64

st.set_page_config(page_title="Club Lakonn", layout="wide", initial_sidebar_state="collapsed")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

img_logo = get_base64('images/LogoCuerda.jpg')

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-color: #0e1117; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .portada {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        display: flex; justify-content: center; align-items: center;
    }}
    /* Triángulo invisible para el clic */
    .stButton>button {{
        position: fixed; top: 35%; left: 35%; width: 30%; height: 30%;
        background: transparent !important; color: transparent !important;
        border: none !important; cursor: pointer; z-index: 10;
        clip-path: polygon(50% 100%, 0 0, 100% 0);
    }}
    .stButton>button:hover {{ background: rgba(255,255,255,0.1) !important; }}
    </style>
    <div class="portada"><img src="data:image/jpg;base64,{img_logo}" style="max-width:100%; max-height:100%; object-fit: contain;"></div>
    """, unsafe_allow_html=True
)

if st.button("Entrar", key="trigger"):
    st.switch_page("pages/login_page.py")
