import streamlit as st

from modulos.consulta_patrimonio import (
    render_patrimonio,
    carregar_dataFrameBaixas
)

from modulos.Histórico_Geral import render_historico

from modulos.SaídaEquipamentos import render_saidas

from modulos.RetornoEquipamentos import render_retornos

from modulos.sup_dash import render_sup

from modulos.estoque_dash import render_estoque


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
    st.session_state["menu_atual"] = "🔍 Consulta Patrimônio"


# ============================================================
# 3. FUNÇÃO DE LOGIN
# ============================================================

def realizar_login(usuario, senha):

    USUARIO_CORRETO = "admin"

    SENHA_CORRETA = "admin123"


    if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:

        st.session_state.autenticado = True

        st.success("Login realizado com sucesso!")

        st.rerun()

    else:

        st.error("Usuário ou senha incorretos.")


# ============================================================
# 4. LOGIN
# ============================================================

if not st.session_state.autenticado:

    # --------------------------------------------------------
    # CSS SOMENTE PARA ORGANIZAÇÃO DO LOGIN
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        .login-container {
            margin-top: 80px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


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

    # ========================================================
    # CSS DA SIDEBAR
    # ========================================================

    st.markdown(
        """
        <style>

        /* ====================================================
           TÍTULO DA SIDEBAR
           ==================================================== */

        [data-testid="stSidebar"] h1 {

            font-size: 1.35rem !important;

            font-weight: 750 !important;

            margin-bottom: 0.2rem !important;
        }


        /* ====================================================
           CAPTION DA SIDEBAR
           ==================================================== */

        [data-testid="stSidebar"]
        [data-testid="stCaptionContainer"] {

            opacity: 0.70;
        }


        /* ====================================================
           BOTÕES DA SIDEBAR
           ==================================================== */

        [data-testid="stSidebar"] .stButton button {

            border-radius: 8px !important;

            min-height: 42px !important;

            transition:
                background-color 0.15s ease,
                border-color 0.15s ease !important;
        }


        /* ====================================================
           BOTÃO ATIVO
           ==================================================== */

        [data-testid="stSidebar"]
        .stButton button[kind="primary"] {

            box-shadow:
                0 2px 8px
                rgba(214, 107, 107, 0.18) !important;
        }


        /* ====================================================
           DIVISOR
           ==================================================== */

        [data-testid="stSidebar"] hr {

            margin-top: 12px;

            margin-bottom: 12px;
        }


        /* ====================================================
           TÍTULOS PRINCIPAIS
           ==================================================== */

        h1 {

            font-weight: 750 !important;

            letter-spacing: -0.5px;
        }


        h2,
        h3 {

            font-weight: 650 !important;
        }


        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        # ----------------------------------------------------
        # IDENTIDADE
        # ----------------------------------------------------

        st.title("🖥️ TI CONTROLE")

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


        paginas_disponiveis = [

            "🔍 Consulta Patrimônio",

            "➡️ Saída Equipamentos",

            "↩️ Retorno Equipamentos",

            "🕒 Histórico Geral",

            "📊 Dashboard Estoque",

            "📈 Dashboard Sup",

            "🗑️ Saídas (Histórico)"
        ]


        # ----------------------------------------------------
        # MENU
        # ----------------------------------------------------

        for pagina in paginas_disponiveis:

            is_active = (
                st.session_state["menu_atual"]
                == pagina
            )


            if st.button(
                pagina,
                use_container_width=True,
                type=(
                    "primary"
                    if is_active
                    else "secondary"
                )
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


        st.caption(
            "VPS Ativos v1.1.0"
        )


    # ========================================================
    # 6. PÁGINA ATUAL
    # ========================================================

    opcao = st.session_state["menu_atual"]


    # ========================================================
    # CONSULTA PATRIMÔNIO
    # ========================================================

    if opcao == "🔍 Consulta Patrimônio":

        st.title(
            "Consulta Patrimônio"
        )

        st.caption(
            "Gerencie e rastreie os ativos de TI em tempo real"
        )

        st.divider()

        render_patrimonio()


    # ========================================================
    # CONSULTA DE BAIXADOS
    # ========================================================

    elif opcao == "🗑️ Saídas (Histórico)":

        st.title(
            "Consulta Baixados"
        )

        st.caption(
            "Ativos desativados e baixados do inventário"
        )

        st.divider()


        df = carregar_dataFrameBaixas()


        if not df.empty:

            st.markdown(
                "### 🔎 Consulta de Baixados"
            )


            filtro = st.text_input(
                "Consultar Plaqueta ou Descrição"
            ).strip().upper()


            if filtro:

                df_filtrado = (

                    df[
                        df["Plaqueta"].str.contains(
                            filtro,
                            case=False,
                            na=False
                        )
                        |
                        df["Desc. Bem"].str.contains(
                            filtro,
                            case=False,
                            na=False
                        )
                    ]

                )

            else:

                df_filtrado = df


            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.warning(
                "Banco de Baixados não disponível ou vazio."
            )


    # ========================================================
    # SAÍDA EQUIPAMENTOS
    # ========================================================

    elif opcao == "➡️ Saída Equipamentos":

        render_saidas()


    # ========================================================
    # RETORNO EQUIPAMENTOS
    # ========================================================

    elif opcao == "↩️ Retorno Equipamentos":

        render_retornos()


    # ========================================================
    # HISTÓRICO GERAL
    # ========================================================

    elif opcao == "🕒 Histórico Geral":

        render_historico()


    # ========================================================
    # DASHBOARD ESTOQUE
    # ========================================================

    elif opcao == "📊 Dashboard Estoque":

        render_estoque()


    # ========================================================
    # DASHBOARD SUP
    # ========================================================

    elif opcao == "📈 Dashboard Sup":

        render_sup()