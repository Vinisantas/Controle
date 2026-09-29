"""Estilos reutilizáveis da interface Streamlit."""

import streamlit as st


def aplicar_estilos_login():
    """Aplica os estilos exclusivos da tela de login."""
    st.markdown(
        """
        <style>
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        .login-container { margin-top: 80px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def aplicar_estilos_sistema():
    """Aplica os ajustes visuais da navegação e dos títulos."""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] h1 {
            font-size: 1.35rem !important;
            font-weight: 750 !important;
            margin-bottom: 0.2rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            opacity: 0.70;
        }
        [data-testid="stSidebar"] .stButton button {
            border-radius: 8px !important;
            min-height: 42px !important;
            transition: background-color 0.15s ease, border-color 0.15s ease !important;
        }
        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            box-shadow: 0 2px 8px rgba(246,43,51,0.18) !important;
        }
        [data-testid="stSidebar"] hr {
            margin-top: 12px;
            margin-bottom: 12px;
        }
        h1 { font-weight: 750 !important; letter-spacing: -0.5px; }
        h2, h3 { font-weight: 650 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
