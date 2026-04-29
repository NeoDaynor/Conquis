import base64

import streamlit as st


st.set_page_config(
    page_title="Club Lakonn - Menu",
    layout="wide",
    initial_sidebar_state="collapsed",
)


if not st.session_state.get("authenticated", False):
    st.switch_page("pages/login_page.py")


def get_base64(path):
    try:
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except OSError:
        return ""


def open_placeholder(section, title, description):
    st.session_state["menu_placeholder"] = {
        "section": section,
        "title": title,
        "description": description,
    }
    st.switch_page("pages/biblioteca.py")


def open_registro_unidades(nivel):
    st.session_state["nivel_tarjeta"] = nivel
    st.switch_page("pages/registro_unidades.py")


user = st.session_state.get("user_info", {"nombre": "Usuario", "rol": "user"})
bg_pc = get_base64("images/fondopc.jpg")
bg_mobile = get_base64("images/fondocelu.webp")
logo = get_base64("images/LogoLakonn.png")

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header, .stAppDeployButton {{
        visibility: hidden;
    }}

    .stApp {{
        background:
            linear-gradient(135deg, rgba(7, 22, 43, 0.88), rgba(7, 61, 120, 0.72)),
            url("data:image/jpg;base64,{bg_pc}") center/cover fixed;
        color: #f6f8fb;
    }}

    @media (max-width: 768px) {{
        .stApp {{
            background:
                linear-gradient(180deg, rgba(7, 22, 43, 0.92), rgba(7, 61, 120, 0.76)),
                url("data:image/webp;base64,{bg_mobile}") center/cover fixed;
        }}
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

logo_html = (
    f'<div class="hero-logo"><img src="data:image/png;base64,{logo}" alt="Club Lakonn"></div>'
    if logo
    else '<div class="hero-logo"></div>'
)

st.markdown(
    f"""
    <div class="hero-shell">
        <div class="hero-top">
            {logo_html}
            <div>
                <p class="hero-eyebrow">Panel principal</p>
                <h1 class="hero-title">Club Lakonn</h1>
                <p class="hero-subtitle">
                    Menu central con acceso claro a administracion, tarjetas progresivas,
                    recursos y especialidades.
                </p>
            </div>
        </div>
        <div class="pill-row">
            <span class="info-pill">Hola de nuevo {user.get("nombre", "Usuario")}</span>
            <span class="info-pill">Tu correo es: {user.get("correo", "Correo")}</span>
            <span class="info-pill">Te desempeñas como: {user.get("rol", "rol").upper()}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([3, 1])

with top_left:
    st.markdown('<p class="section-label">Accesos rapidos</p>', unsafe_allow_html=True)

with top_right:
    if st.button("Cerrar sesion", key="logout_top", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user_info", None)
        st.switch_page("app.py")

if user.get("rol") == "admin":
    st.markdown('<p class="section-label">Administracion de Usuarios</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="section-card">
                <span class="mini-label">Administracion</span>
                <h3>Gestion de usuarios del sistema</h3>
                <p>Acceso directo para crear, editar y mantener cuentas internas del club.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with top_left:
            if st.button("Abrir administracion de usuarios", key="go_admin", use_container_width=True):
                st.switch_page("pages/gestion_usuarios.py")

st.markdown('<p class="section-label">Tarjetas Progresivas</p>', unsafe_allow_html=True)
with st.expander("Amigo", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <span class="mini-label">Tarjeta progresiva</span>
            <h4>Ruta de trabajo: Amigo</h4>
            <p>Accesos organizados para gestionar el progreso, la documentacion y el material de apoyo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    a_col1, a_col2, a_col3 = st.columns(3)
    with a_col1:
        if st.button("Registro Unidades", key="amigo_registro", use_container_width=True):
            open_registro_unidades("Amigo")        
        
        st.link_button(
        "📓 Abrir Cuadernillo PDF", 
        "https://drive.google.com/file/d/16r__Nuf-c7sx8cEtU60Ts-6leMD0U1sr/view?usp=sharing", 
        use_container_width=True
        )
        
        #if st.button("Registro Unidades", key="amigo_registro", use_container_width=True):
        #    open_registro_unidades("Amigo")
            
        # ===== CÓDIGO ANTERIOR COMENTADO (PROTOCOLO NO BORRADO) =====
        # if st.button("Cuadernillo", key="amigo_cuadernillo", use_container_width=True):
        #     open_placeholder(
        #         "Tarjetas progresivas / Amigo",
        #         "Cuadernillo de Amigo",
        #         "Espacio preparado para alojar el cuadernillo digital, contenidos y seguimiento de trabajo.",
        #     )
        # ============================================================
        
        # ===== NUEVO CÓDIGO =====
        #if st.button("📓 Cuadernillo", key="amigo_cuadernillo_link", use_container_width=True):
        #    st.switch_page("pages/cuadernillo_amigo.py")
        # ========================
            
    with a_col2:
# ===== CÓDIGO ANTERIOR COMENTADO (PROTOCOLO NO BORRADO) =====
        # if st.button("Tarjeta", key="amigo_tarjeta", use_container_width=True):
        #     open_placeholder(
        #         "Tarjetas progresivas / Amigo",
        #         "Tarjeta de Amigo",
        #         "Vista reservada para mostrar, imprimir o validar la tarjeta progresiva de la clase Amigo.",
        #     )
        # ============================================================

        # ===== NUEVO BOTÓN: TARJETA DE AMIGO (PDF) =====
        st.link_button(
            "💳 Abrir Tarjeta de Amigo", 
            "https://drive.google.com/file/d/1812uegmnFCSG1CUl4SFSTzXNvbDAEMM0/view?usp=drive_link", 
            use_container_width=True
        )

        # ===== NUEVO BOTÓN: LIBRO POR LA GRACIA DE DIOS =====
        st.link_button(
            "📖 Libro: Por la gracia de Dios", 
            "https://drive.google.com/file/d/1rNuZk_dLsz6XMluzcebawFU89hNAc2L2/view?usp=drive_link", 
            use_container_width=True
        )
        # ===================================================
    with a_col3:
        # ===== NUEVO BOTÓN: EL HACHA Y EL CUCHILLO =====
        st.link_button(
            "🪓 Especialidad: El hacha y el cuchillo", 
            "https://drive.google.com/file/d/1j-WXa0Rtzq8S24Nk1heG7sOtmxfzWGkA/view?usp=drive_link", 
            use_container_width=True
        )
        # ===============================================
        # ===== NUEVO BOTÓN: VOTO Y LA LEY =====
        st.link_button(
            "📜 Voto y la Ley", 
            "https://drive.google.com/file/d/1SdwWARDUB9TcnYjjPPaWVRX5zieS4Exa/view?usp=drive_link", 
            use_container_width=True
        )
        # =====================================

with st.expander("Companero", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <span class="mini-label">Tarjeta progresiva</span>
            <h4>Ruta de trabajo: Companero</h4>
            <p>Estructura lista para continuar la siguiente etapa del programa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        if st.button("Registro Unidades", key="companero_registro", use_container_width=True):
            open_registro_unidades("Companero")
        if st.button("Cuadernillo", key="companero_cuadernillo", use_container_width=True):
            open_placeholder(
                "Tarjetas progresivas / Companero",
                "Cuadernillo de Companero",
                "Seccion preparada para el cuadernillo de la clase Companero y su futura navegacion.",
            )
    with c_col2:
        if st.button("Tarjeta", key="companero_tarjeta", use_container_width=True):
            open_placeholder(
                "Tarjetas progresivas / Companero",
                "Tarjeta de Companero",
                "Vista reservada para la tarjeta progresiva de Companero y su posterior integracion.",
            )
        if st.button("Material de Apoyo", key="companero_material", use_container_width=True):
            open_placeholder(
                "Tarjetas progresivas / Companero",
                "Material de Apoyo - Companero",
                "Area disponible para recursos metodologicos, descargables y apoyo de clase.",
            )

st.markdown('<p class="section-label">Recursos</p>', unsafe_allow_html=True)
with st.expander("Manuales", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <span class="mini-label">Recursos</span>
            <h4>Biblioteca General</h4>
            <p>Acceso pensado para concentrar documentos, instructivos, libros y referencia institucional.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Abrir nuestra Biblioteca", key="biblioteca", use_container_width=True):
        open_placeholder(
            "Recursos",
            "Biblioteca",
            "En esta sección encontraras manuales internos, documentos PDF, Libros y apoyos para nuestro club.",
        )

st.markdown('<p class="section-label">Especialidades</p>', unsafe_allow_html=True)
with st.expander("Catalogo de especialidades", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <span class="mini-label">Especialidades</span>
            <h4>Rutas de aprendizaje practico</h4>
            <p>Menu preparado para abrir contenidos, guias y seguimiento por especialidad.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        if st.button("Nudos", key="esp_nudos", use_container_width=True):
            open_placeholder(
                "Especialidades",
                "Nudos",
                "Espacio preparado para teoria, materiales y avances de la especialidad de Nudos.",
            )
        if st.button("Amarras", key="esp_amarras", use_container_width=True):
            open_placeholder(
                "Especialidades",
                "Amarras",
                "Seccion lista para desarrollar el contenido, practicas y material de apoyo de Amarras.",
            )
    with e_col2:
        if st.button("Arte de Acampar", key="esp_arte", use_container_width=True):
            open_placeholder(
                "Especialidades",
                "Arte de Acampar",
                "Vista diseñada para reunir contenidos, requisitos y recursos de Arte de Acampar.",
            )
        if st.button("Campamento 1", key="esp_camp1", use_container_width=True):
            open_placeholder(
                "Especialidades",
                "Campamento 1",
                "Area preparada para checklist, contenidos y evidencias relacionadas con Campamento 1.",
            )

st.markdown(
    '<p class="muted-note">Algunas secciones se mantienen en construcción.</p>',
    unsafe_allow_html=True,
)
