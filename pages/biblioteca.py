import streamlit as st

from ui_theme import apply_app_theme, render_hero


st.set_page_config(
    page_title="Club Lakonn - Biblioteca",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")

data = st.session_state.get(
    "menu_placeholder",
    {
        "section": "Menu",
        "title": "Seccion disponible",
        "description": "Esta vista queda preparada para continuar la implementacion.",
    },
)

apply_app_theme(max_width=980)

render_hero(
    data.get("title", "Seccion disponible"),
    data.get("description", ""),
    eyebrow=data.get("section", "Menu"),
)

st.markdown(
    '<p class="muted-note">Ultima actualización Abril - 2026.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header, .stAppDeployButton {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1100px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }}

    .hero-shell {{
        background: linear-gradient(145deg, rgba(7, 22, 43, 0.82), rgba(15, 84, 153, 0.68));
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 28px;
        padding: 28px;
        box-shadow: 0 24px 60px rgba(5, 10, 20, 0.28);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }}

    .hero-top {{
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }}

    .hero-logo {{
        width: 84px;
        height: 84px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.16);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        flex-shrink: 0;
    }}

    .hero-logo img {{
        width: 76%;
        height: 76%;
        object-fit: contain;
    }}

    .hero-eyebrow {{
        letter-spacing: 0.18em;
        text-transform: uppercase;
        font-size: 0.78rem;
        color: #9ed0ff;
        margin: 0 0 0.45rem 0;
    }}

    .hero-title {{
        font-size: clamp(2rem, 5vw, 3.35rem);
        line-height: 1;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }}

    .hero-subtitle {{
        margin: 0.7rem 0 0 0;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.82);
        max-width: 760px;
    }}

    .pill-row {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 1rem;
    }}

    .info-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0.6rem 0.9rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.14);
        color: #eef6ff;
        font-size: 0.92rem;
    }}

    .section-label {{
        margin-top: 1.6rem;
        margin-bottom: 0.55rem;
        font-size: 0.82rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #b8dbff;
    }}

    .stExpander {{
        border: 0 !important;
        background: transparent !important;
    }}

    .stExpander details {{
        border-radius: 22px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        background: rgba(8, 20, 38, 0.62) !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 18px 45px rgba(5, 10, 20, 0.2);
        overflow: hidden;
    }}

    .stExpander summary {{
        padding: 1rem 1.15rem !important;
        font-size: 1.08rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }}

    .stExpander summary:hover {{
        background: rgba(255, 255, 255, 0.05);
    }}

    .section-card {{
        border-radius: 22px;
        padding: 20px;
        background: linear-gradient(160deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 255, 255, 0.12);
        margin-bottom: 16px;
    }}

    .section-card h3,
    .section-card h4 {{
        margin: 0;
        color: #ffffff;
    }}

    .section-card p {{
        margin: 0.55rem 0 0 0;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.55;
    }}

    .mini-label {{
        display: inline-block;
        margin-bottom: 0.8rem;
        font-size: 0.76rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #9ed0ff;
    }}

/* Estilo unificado para botones normales y botones de enlace */
    div.stButton > button, div.stLinkButton > a {{
        width: 100%;
        min-height: 3rem;
        border-radius: 14px !important;
        border: 1px solid rgba(125, 196, 255, 0.45) !important;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(236, 244, 255, 0.96)) !important;
        color: #0f3660 !important;
        font-weight: 600 !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
        box-shadow: 0 12px 24px rgba(8, 22, 43, 0.18);
        
        /* Ajustes extra para que el enlace se comporte como botón */
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
    }}

    div.stButton > button:hover, div.stLinkButton > a:hover {{
        transform: translateY(-2px);
        box-shadow: 0 16px 26px rgba(8, 22, 43, 0.24);
        border-color: rgba(15, 84, 153, 0.8) !important;
        color: #0a2a49 !important;
        text-decoration: none !important;
    }}

    .muted-note {{
        font-size: 0.93rem;
        color: rgba(255, 255, 255, 0.72);
        margin-top: 0.7rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="section-label">Biblioteca</p>', unsafe_allow_html=True)
##---------------- Esta seccion estan libros ----------------------------------------------------------------------------
with st.expander("Libros", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <span class="mini-label">Biblioteca Cristiana</span>
            <h4>Libros</h4>
            <p>Aca encontrarás libros en pdf, recomendado para Jovenes y Adultos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    a_col1, a_col2, a_col3 = st.columns(3)
    with a_col1:
        st.link_button(
        "📖 Libro: El Camino a Cristo", 
        "https://drive.google.com/file/d/1vtzee5IZWp0GYVMGifhj914obBzus6hE/view?usp=drive_link", 
        use_container_width=True
        )        
        
        st.link_button(
        "📖 Libro: El Hogar Cristiano", 
        "https://drive.google.com/file/d/1qpjPsger0WM4RkOPlWl6m9DWYxg5J2pS/view?usp=drive_link", 
        use_container_width=True
        )
        
    with a_col2:
        st.link_button(
            "📖 Libro: El Ministerio de la Bondad", 
            "https://drive.google.com/file/d/12C_Ei44YCgx_k2z3MN-KxZaDHzlugEbg/view?usp=drive_link", 
            use_container_width=True
        )

        st.link_button(
            "📖 Libro: Por la gracia de Dios", 
            "https://drive.google.com/file/d/1rNuZk_dLsz6XMluzcebawFU89hNAc2L2/view?usp=drive_link", 
            use_container_width=True
        )

    with a_col3:
        st.link_button(
            "📖 Libro: Mente, Carácter y Personalidad TOMO 1", 
            "https://drive.google.com/file/d/1GBFIPS8oDQekNVAP4flwwyo_CYD8Kr31/view?usp=drive_link", 
            use_container_width=True
        )

        st.link_button(
            "📖 Libro: Mente, Carácter y Personalidad TOMO 2", 
            "https://drive.google.com/file/d/1RSjyw1p11riYDlpYdHbp94YLQjmZE-Ml/view?usp=drive_link", 
            use_container_width=True
        )

##---------------- Esta seccion estan los Manuales ----------------------------------------------------------------------------
with st.expander("Manuales", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <span class="mini-label">Biblioteca Cristiana</span>
            <h4>Libros</h4>
            <p>Aca encontrarás libros en pdf, recomendado para Jovenes y Adultos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    a_col1, a_col2 = st.columns(2)
    with a_col1:
        st.link_button(
        "📓 Manual: Manual de nudos conquistadores", 
        "https://drive.google.com/file/d/1pGfY42P-pq_lMjp52LflRVvO6hIiyNwt/view?usp=drive_link", 
        use_container_width=True
        )        
        
        st.link_button(
        "📓 Manual: Manual de nudos y mas", 
        "https://drive.google.com/file/d/1YYmP563-J6IzFg0ULCmr20Qp9vaF1mxe/view?usp=drive_link", 
        use_container_width=True
        )
        
    with a_col2:
        st.link_button(
            "📓 Manual: Manual de nudos", 
            "https://drive.google.com/file/d/1Znb_FyYMnzmYfZxnL71ErHlcaEEXA8Te/view?usp=drive_link", 
            use_container_width=True
        )

        st.link_button(
            "📓 Manual: El hacha y El cuchillo", 
            "https://drive.google.com/file/d/1wowlzagO0Tfg69dKV7bQY18pP2o9ZV3i/view?usp=drive_link", 
            use_container_width=True
        )




col1, col2 = st.columns(2)
with col1:
    if st.button("Volver al menu", use_container_width=True):
        st.switch_page("pages/menu.py")
with col2:
    if st.button("Cerrar sesion", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user_info", None)
        st.switch_page("app.py")
