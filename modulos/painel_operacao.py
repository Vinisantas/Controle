"""Central de operações da Gestão de Ativos TI."""

import streamlit as st

from modulos.busca_universal import render_busca_universal


def _abrir(pagina: str) -> None:
    st.session_state["menu_atual"] = pagina
    st.rerun()


def _acao(icone: str, titulo: str, descricao: str, pagina: str, chave: str) -> None:
    st.markdown(
        f"""
        <div class="vs-action-card">
            <div class="vs-action-icon">{icone}</div>
            <div class="vs-action-title">{titulo}</div>
            <div class="vs-action-desc">{descricao}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Abrir →", key=f"acao_{chave}", use_container_width=True):
        _abrir(pagina)


def render_painel_operacao() -> None:
    st.markdown(
        """
        <style>
        .ops-wrap { max-width: 1180px; margin: 0 auto; padding-top: 4px; }

        .ops-hero {
            position: relative;
            overflow: hidden;
            padding: 30px 32px 28px;
            border-radius: 18px;
            background:
                radial-gradient(circle at 92% 20%, rgba(201,47,55,.18), transparent 28%),
                linear-gradient(135deg, #0D1B22 0%, #071116 72%);
            border: 1px solid #263B44;
            box-shadow: 0 20px 55px rgba(0,0,0,.22);
            margin-bottom: 24px;
        }
        .ops-hero-kicker {
            color: #D65A61;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }
        .ops-hero-title {
            color: #F8FAFB;
            font-size: 31px;
            line-height: 1.1;
            font-weight: 850;
            letter-spacing: -.9px;
            margin: 0;
        }
        .ops-hero-text {
            color: #91A0A6;
            font-size: 13px;
            line-height: 1.55;
            margin-top: 9px;
            max-width: 690px;
        }

        .search-panel {
            padding: 21px 23px 19px;
            border-radius: 15px;
            background: #0A171E;
            border: 1px solid #2A414A;
            box-shadow: 0 13px 32px rgba(0,0,0,.17);
            margin-bottom: 28px;
        }
        .search-title {
            color: #F7F9FA;
            font-size: 16px;
            font-weight: 750;
            margin-bottom: 3px;
        }
        .search-desc {
            color: #84949B;
            font-size: 12px;
            margin-bottom: 13px;
        }

        .ops-section {
            color: #AAB7BC;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.7px;
            margin: 0 0 12px;
        }
        .vs-action-card {
            min-height: 132px;
            padding: 20px 20px 17px;
            border-radius: 15px;
            background: linear-gradient(145deg, #0B1920, #071116);
            border: 1px solid #243842;
            box-shadow: 0 13px 32px rgba(0,0,0,.15);
            margin-bottom: 8px;
        }
        .vs-action-icon { font-size: 23px; margin-bottom: 11px; }
        .vs-action-title {
            color: #F4F7F8;
            font-size: 16px;
            font-weight: 750;
            margin-bottom: 5px;
        }
        .vs-action-desc {
            color: #84949B;
            font-size: 11.5px;
            line-height: 1.45;
        }

        div[data-testid="stTextInput"] input {
            background: #07141A !important;
            border: 1px solid #304750 !important;
            border-radius: 9px !important;
            color: #F7F9FA !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #B9363D !important;
            box-shadow: 0 0 0 2px rgba(185,54,61,.13) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ops-wrap">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="ops-hero">
            <div class="ops-hero-kicker">VS. • GESTÃO DE ATIVOS TI</div>
            <div class="ops-hero-title">Central de Operações</div>
            <div class="ops-hero-text">
                Consulte um patrimônio ou escolha uma operação. O sistema deve cuidar
                do máximo de informações possível para você.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    render_busca_universal()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ops-section">OPERAÇÕES</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        _acao(
            "📤", "Enviar equipamento",
            "Envie um ativo para loja, setor ou outro destino.",
            "➡️ Saída Equipamentos", "enviar",
        )
    with c2:
        _acao(
            "📥", "Receber equipamento",
            "Registre a chegada de um equipamento ao estoque ou setor.",
            "↩️ Retorno Equipamentos", "receber",
        )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        _acao(
            "🔧", "Enviar para assistência",
            "Registre uma manutenção ou atendimento técnico.",
            "🛠️ Assistências", "assistencia",
        )
    with c4:
        _acao(
            "🧭", "Histórico de movimentações",
            "Acompanhe as movimentações registradas dos equipamentos.",
            "🕒 Histórico Geral", "historico",
        )

    st.markdown('</div>', unsafe_allow_html=True)
