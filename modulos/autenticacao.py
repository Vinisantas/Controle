"""Autenticação da interface de Gestão de Ativos TI."""

import os
import streamlit as st


def realizar_login(usuario, senha):
    """Valida as credenciais configuradas no ambiente."""
    usuario_correto = os.getenv("APP_USUARIO", "")
    senha_correta = os.getenv("APP_SENHA", "")

    if usuario_correto and senha_correta and usuario == usuario_correto and senha == senha_correta:
        st.session_state.autenticado = True
        st.session_state["usuario_logado"] = usuario.strip()
        st.success("Login realizado com sucesso!")
        st.rerun()
    else:
        st.error("Usuário ou senha incorretos.")
