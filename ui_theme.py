import base64

import streamlit as st


def get_base64(path):
    try:
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except OSError:
        return ""


def apply_app_theme(max_width=1100):
    bg_pc = get_base64("images/fondopc.jpg")
    bg_mobile = get_base64("images/fondocelu.webp")

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
            max-width: {max_width}px;
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

        .section-card {{
            border-radius: 22px;
            padding: 20px;
            background: linear-gradient(160deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.03));
            border: 1px solid rgba(255, 255, 255, 0.12);
            margin-bottom: 16px;
            box-shadow: 0 18px 45px rgba(5, 10, 20, 0.16);
            backdrop-filter: blur(8px);
        }}

        .section-card h3,
        .section-card h4,
        .section-card p,
        .section-card label {{
            color: #ffffff !important;
        }}

        .section-card p {{
            margin: 0.55rem 0 0 0;
            color: rgba(255, 255, 255, 0.82) !important;
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

        .muted-note {{
            font-size: 0.93rem;
            color: rgba(255, 255, 255, 0.72);
            margin-top: 0.7rem;
        }}

        div.stButton > button,
        button[kind="primaryFormSubmit"] {{
            width: 100%;
            min-height: 3rem;
            border-radius: 14px !important;
            border: 1px solid rgba(125, 196, 255, 0.45) !important;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(236, 244, 255, 0.96)) !important;
            color: #0f3660 !important;
            font-weight: 600 !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
            box-shadow: 0 12px 24px rgba(8, 22, 43, 0.18);
        }}

        div.stButton > button:hover,
        button[kind="primaryFormSubmit"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 16px 26px rgba(8, 22, 43, 0.24);
            border-color: rgba(15, 84, 153, 0.8) !important;
            color: #0a2a49 !important;
        }}

        [data-testid="stForm"] {{
            border-radius: 22px !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            background: rgba(8, 20, 38, 0.62) !important;
            box-shadow: 0 18px 45px rgba(5, 10, 20, 0.2);
            padding: 1.2rem !important;
        }}

        [data-testid="stForm"] label,
        [data-testid="stForm"] p,
        [data-testid="stForm"] h1,
        [data-testid="stForm"] h2,
        [data-testid="stForm"] h3,
        [data-testid="stForm"] h4 {{
            color: #ffffff !important;
        }}

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] {{
            background: rgba(255, 255, 255, 0.94) !important;
            color: #102b4a !important;
            border-radius: 14px !important;
        }}

        .stDataFrame,
        [data-testid="stDataFrame"] {{
            border-radius: 18px !important;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }}

        .stAlert {{
            border-radius: 18px !important;
        }}

        .stMarkdown,
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown label,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4 {{
            color: #ffffff;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title, subtitle, eyebrow="Panel principal", pills=None, logo_path="images/LogoLakonn.png"):
    logo = get_base64(logo_path) if logo_path else ""
    logo_html = (
        f'<div class="hero-logo"><img src="data:image/png;base64,{logo}" alt="Club Lakonn"></div>'
        if logo
        else '<div class="hero-logo"></div>'
    )
    pills_html = ""
    if pills:
        pills_html = '<div class="pill-row">' + "".join(
            f'<span class="info-pill">{pill}</span>' for pill in pills
        ) + "</div>"

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-top">
                {logo_html}
                <div>
                    <p class="hero-eyebrow">{eyebrow}</p>
                    <h1 class="hero-title">{title}</h1>
                    <p class="hero-subtitle">{subtitle}</p>
                </div>
            </div>
            {pills_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_card():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)


def close_card():
    st.markdown("</div>", unsafe_allow_html=True)
