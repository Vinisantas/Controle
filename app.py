from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from modulos.navegacao import renderizar_pagina
from modulos.estilos import aplicar_estilos_login, aplicar_estilos_sistema
from modulos.autenticacao import realizar_login


# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Controle de Ativos TI",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. ESTADO DA APLICAÇÃO
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


if "menu_atual" not in st.session_state:
    st.session_state["menu_atual"] = "🏠 Visão Geral"


# ============================================================
# 4. LOGIN
# ============================================================

if not st.session_state.autenticado:

    aplicar_estilos_login()


    # --------------------------------------------------------
    # CENTRALIZA LOGIN
    # --------------------------------------------------------

    _, col_login, _ = st.columns(
        [1.2, 1.5, 1.2]
    )


    with col_login:

        st.write("")


        # ----------------------------------------------------
        # CABEÇALHO
        # ----------------------------------------------------

        st.title("🔐 TI CONTROLE")

        st.caption(
            "VPS Tech - Gestão Patrimonial"
        )


        st.write("")


        # ----------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------

        with st.form("form_login"):

            usuario_input = st.text_input(
                "Usuário",
                placeholder="Digite seu usuário"
            )


            senha_input = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha"
            )


            botao_entrar = st.form_submit_button(
                "Entrar no Sistema",
                use_container_width=True
            )


            if botao_entrar:

                realizar_login(
                    usuario_input,
                    senha_input
                )


# ============================================================
# 5. SISTEMA PRINCIPAL
# ============================================================

else:

    with open(r"vs_style.css", encoding="utf-8") as f:
        st.markdown("<style>"+f.read()+"</style>", unsafe_allow_html=True)

    aplicar_estilos_sistema()


    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        # ----------------------------------------------------
        # IDENTIDADE
        # ----------------------------------------------------

        st.markdown("""<div class="vs-brand"><div class="vs-logo">VS<span>.</span></div><div class="vs-product">Controle de Ativos TI</div></div>""", unsafe_allow_html=True)

        st.caption(
            "Gestão de Equipamentos"
        )


        st.divider()


        # ----------------------------------------------------
        # USUÁRIO
        # ----------------------------------------------------

        st.caption(
            "USUÁRIO ATIVO"
        )

        st.markdown(
            "**🔴 admin**"
        )


        st.divider()


        # ----------------------------------------------------
        # NAVEGAÇÃO
        # ----------------------------------------------------

        st.caption(
            "NAVEGAÇÃO PRINCIPAL"
        )


        grupos_menu = {
            "OPERAÇÃO": [
                "🏠 Visão Geral",
                "🔍 Consulta Patrimônio",
                "➡️ Saída Equipamentos",
                "↩️ Retorno Equipamentos",
                "🛠️ Assistências",
            ],
            "ACOMPANHAMENTO": [
                "📊 Central de Dashboards",
                "🕒 Histórico Geral",
                "📊 Dashboard Estoque",
                "📈 Dashboard Sup",
                "🤖 Assistente de TI",
            ],
            "ADMINISTRAÇÃO": [
                "📥 Importação Senior",
                "🗑️ Saídas (Histórico)",
            ],
        }

        # ----------------------------------------------------
        # MENU AGRUPADO POR RESPONSABILIDADE
        # ----------------------------------------------------
        for grupo, paginas in grupos_menu.items():
            st.caption(grupo)
            for pagina in paginas:
                is_active = st.session_state["menu_atual"] == pagina
                if st.button(
                    pagina,
                    key=f"menu_{pagina}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state["menu_atual"] = pagina
                    st.rerun()


        st.divider()


        # ----------------------------------------------------
        # SAIR
        # ----------------------------------------------------

        if st.button(
            "🚪 Sair do Sistema",
            use_container_width=True
        ):

            st.session_state.autenticado = False

            st.rerun()


        st.caption("VS. Controle de Ativos TI • v1.1.0")


    # ========================================================
    # 6. RENDERIZAÇÃO DA PÁGINA SELECIONADA
    # ========================================================

    opcao = st.session_state["menu_atual"]
    renderizar_pagina(opcao)
