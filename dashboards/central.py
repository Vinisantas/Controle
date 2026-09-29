"""Central de acesso aos dashboards operacionais, sem consultas ou gravações."""
import streamlit as st


def _abrir_pagina(pagina):
    st.session_state["menu_atual"] = pagina


def render_central_dashboards():
    st.title("📊 Central de Dashboards TI")
    st.caption("Acompanhamento operacional em um único lugar")
    st.divider()

    st.info(
        "Escolha uma visão para acompanhar a operação. Esta central é somente de navegação; "
        "não altera registros patrimoniais nem executa cargas do BI."
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.markdown("### 📦 Estoque e solicitações")
            st.caption("Visão operacional com indicadores de estoque, solicitações e integrações disponíveis.")
            st.markdown(
                "- Acompanhamento de solicitações\n"
                "- Indicadores de status\n"
                "- Integrações Movidesk e Asana, conforme disponibilidade"
            )
            st.button(
                "Abrir Dashboard Estoque",
                key="central_abrir_estoque",
                type="primary",
                use_container_width=True,
                on_click=_abrir_pagina,
                args=("📊 Dashboard Estoque",),
            )

    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Suporte técnico")
            st.caption("Visão de chamados de suporte e acompanhamento da equipe.")
            st.markdown(
                "- Chamados e status\n"
                "- Acompanhamento do atendimento\n"
                "- Indicadores de suporte"
            )
            st.button(
                "Abrir Dashboard SUP",
                key="central_abrir_suporte",
                type="primary",
                use_container_width=True,
                on_click=_abrir_pagina,
                args=("📈 Dashboard Sup",),
            )

    st.divider()
    st.markdown("### 🧭 Onde cada informação é tratada")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Gestão operacional**")
        st.caption("Cadastros, saídas, retornos e assistências são registrados nas telas de operação.")
    with c2:
        st.markdown("**Dashboards operacionais**")
        st.caption("Consultas para acompanhar estoque, solicitações e suporte.")
    with c3:
        st.markdown("**BI analítico**")
        st.caption("O modelo PostgreSQL e os relatórios Power BI permanecem separados desta aplicação.")
