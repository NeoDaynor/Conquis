import json
import os
from collections import Counter

import streamlit as st

from ui_theme import apply_app_theme, render_hero


st.set_page_config(
    page_title="Gestion de Usuarios - Club Lakonn",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not st.session_state.get("authenticated", False) or st.session_state.get("user_info", {}).get("rol") != "admin":
    st.switch_page("app.py")


def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as file:
            return json.load(file)
    return {"users": []}


def save_users(data):
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


apply_app_theme()

user = st.session_state.get("user_info", {"nombre": "Usuario", "rol": "admin"})
render_hero(
    "Gestion de Usuarios",
    "Administra cuentas internas del club, corrige permisos y mantén ordenado el acceso al sistema con la misma línea visual del panel principal.",
    eyebrow="Administracion",
    pills=[f"Hola de nuevo {user.get('nombre', '')}"
    ,f"Tu correo es {user.get('correo', '')}"
    ,f"Te desempeñas como: {user.get('rol', '').upper()}"
    ],
)

st.markdown(
    """
    <style>
    .st-key-dashboard_wrap,
    .st-key-registro_wrap {
        border-radius: 22px;
        padding: 20px;
        background: linear-gradient(160deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 18px 45px rgba(5, 10, 20, 0.16);
        backdrop-filter: blur(8px);
        margin-bottom: 16px;
    }

    .st-key-dashboard_wrap .section-card,
    .st-key-registro_wrap .section-card {
        background: transparent;
        border: 0;
        box-shadow: none;
        padding: 14px 18px 18px 18px;
        margin-bottom: 0;
    }

    .st-key-dashboard_wrap .section-card h3,
    .st-key-registro_wrap .section-card h3 {
        margin-top: 0.35rem;
        margin-bottom: 1rem;
    }

    .st-key-dashboard_wrap .section-card p,
    .st-key-registro_wrap .section-card p {
        margin-top: 0;
        margin-bottom: 0.4rem;
    }

    .st-key-registro_inner_wrap {
        border-radius: 18px;
        padding: 18px 18px 8px 18px;
        background: rgba(9, 20, 37, 0.52);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        margin-top: 6px;
    }

    .st-key-registro_inner_wrap .stSelectbox,
    .st-key-registro_inner_wrap .stCheckbox,
    .st-key-registro_inner_wrap .stButton {
        position: relative;
        z-index: 1;
    }

        .stExpander {
        border: 0 !important;
        background: transparent !important;
    }

    .stExpander details {
        border-radius: 22px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        background: rgba(8, 20, 38, 0.62) !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 18px 45px rgba(5, 10, 20, 0.2);
        overflow: hidden;
    }

    .stExpander summary {
        padding: 1rem 1.15rem !important;
        font-size: 1.08rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }

    .stExpander summary:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)


top_left, top_right = st.columns(2)
with top_left:
    if st.button("Volver al menu", key="back_menu", use_container_width=True):
        st.switch_page("pages/menu.py")
with top_right:
    if st.button("Cerrar sesion", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("user_info", None)
        st.switch_page("app.py")

data = load_users()
user_ids = [row.get("id") for row in data["users"] if "id" in row]
duplicated_ids = sorted([user_id for user_id, count in Counter(user_ids).items() if count > 1])

with st.expander("Alta de usuarios", expanded=False):
#st.markdown('<p class="section-label">Alta de usuarios</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="section-card">
                <span class="mini-label">Registro</span>
                <h3>Nuevo miembro del sistema</h3>
                <p>Crea una cuenta nueva y asígnale el rol correcto para el flujo administrativo o de seguimiento.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("new_user_form"):
            c1, c2 = st.columns(2)
            new_nombre = c1.text_input("Nombre completo")
            new_cargo = c2.text_input("Cargo")
            new_user = c1.text_input("Usuario (login)")
            new_pass = c2.text_input("Contrasena", type="password")
            new_rol = st.selectbox("Rol de sistema", ["admin", "lider", "conqui"])
    
            if st.form_submit_button("Guardar usuario", use_container_width=True):
                new_id = max([row["id"] for row in data["users"]], default=0) + 1
                data["users"].append(
                    {
                        "id": new_id,
                        "nombre": new_nombre,
                        "cargo": new_cargo,
                        "rol": new_rol,
                        "usuario": new_user,
                        "password": new_pass,
                    }
                )
                save_users(data)
                st.success("Usuario creado correctamente.")
                st.rerun()

with st.expander("Usuarios existentes", expanded=True):
    st.markdown('<p>Edita los datos del miembro, actualiza su rol o elimina el registro si ya no corresponde.</p>', unsafe_allow_html=True)
    
    if duplicated_ids:
        duplicated_ids_text = ", ".join(str(user_id) for user_id in duplicated_ids)
        st.warning(
            f"Se detectaron IDs duplicados en users.json: {duplicated_ids_text}. "
            "La vista sigue operativa porque cada fila usa una clave unica, pero conviene normalizarlos despues."
        )
    
    for idx, row in enumerate(data["users"]):
        with st.container():
            st.markdown(
                f"""
                <div class="section-card">
                    <!--<span class="mini-label">Usuario #{row.get("id", "sin_id")}</span>-->
                    <h4>{row.get("nombre", "Sin nombre")}</h4>
                    
                </div>
                """,
                unsafe_allow_html=True,
            )
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1.5, 0.7])
            row_key = f"{row.get('id', 'sin_id')}_{idx}"
    
            updated_nombre = c1.text_input("Nombre", value=row["nombre"], key=f"nom_{row_key}")
            updated_cargo = c2.text_input("Cargo", value=row["cargo"], key=f"car_{row_key}")
            updated_user = c3.text_input("Usuario", value=row["usuario"], key=f"usr_{row_key}")
            roles = ["admin", "lider", "conqui"]
            default_role_idx = roles.index(row.get("rol", "conqui"))
            updated_rol = c4.selectbox("Rol", roles, index=default_role_idx, key=f"rol_{row_key}")
    
            if c5.button("Eliminar", key=f"del_{row_key}", use_container_width=True):
                data["users"].pop(idx)
                save_users(data)
                st.rerun()
    
            if (
                updated_nombre != row["nombre"]
                or updated_cargo != row["cargo"]
                or updated_user != row["usuario"]
                or updated_rol != row.get("rol")
            ):
                data["users"][idx]["nombre"] = updated_nombre
                data["users"][idx]["cargo"] = updated_cargo
                data["users"][idx]["usuario"] = updated_user
                data["users"][idx]["rol"] = updated_rol
                save_users(data)
                st.toast(f"Actualizado: {updated_nombre}")
