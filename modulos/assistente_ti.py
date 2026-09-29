"""Central operacional de consulta do TI CONTROLE."""

from __future__ import annotations

import streamlit as st

from services import assistente_service


def render_assistente_ti() -> None:
    st.title("🤖 Central de TI")
    st.caption("Consulte rapidamente ativos, movimentações, pendências e situações que precisam de atenção.")

    resumo = assistente_service.carregar_resumo_operacional()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ativos", f"{resumo['ativos']:,}".replace(",", "."))
    col2.metric("Saídas pendentes", resumo["saidas_sem_retorno"])
    col3.metric("Baixas pendentes", resumo["pendencias_baixa"])
    col4.metric("Itens em estoque", f"{resumo['itens_estoque']:,}".replace(",", "."))

    st.markdown("### 🔎 Consulta rápida")
    st.caption("Digite uma plaqueta ou faça uma pergunta simples sobre a operação.")
    pergunta = st.text_input(
        "Consulta",
        placeholder="Ex.: onde está a plaqueta 81940? ou quantos ativos temos?",
        label_visibility="collapsed",
    )
    if pergunta:
        resposta, dados = assistente_service.interpretar_pergunta(pergunta)
        st.info(resposta)
        if dados is not None and not dados.empty:
            st.dataframe(dados, use_container_width=True, hide_index=True)

    st.markdown("### 📋 Acompanhamento operacional")
    tab_pendencias, tab_consulta = st.tabs(["Pendências", "Patrimônio"])

    with tab_pendencias:
        col_a, col_b = st.columns(2)
        saidas = assistente_service.listar_saidas_sem_retorno()
        baixas = assistente_service.listar_pendencias_baixa()

        with col_a:
            st.markdown("#### ➡️ Saídas sem retorno")
            if saidas.empty:
                st.success("Nenhuma saída pendente.")
            else:
                st.dataframe(saidas, use_container_width=True, hide_index=True)

        with col_b:
            st.markdown("#### 🧾 Baixas pendentes")
            if baixas.empty:
                st.success("Nenhuma baixa pendente.")
            else:
                st.dataframe(baixas, use_container_width=True, hide_index=True)

    with tab_consulta:
        plaqueta = st.text_input(
            "Número do patrimônio",
            placeholder="Ex.: 113046",
            key="consulta_assistente",
        )
        if plaqueta:
            ativo = assistente_service.buscar_ativo(plaqueta)
            if ativo.empty:
                st.warning("Plaqueta não localizada no cadastro de patrimônio.")
            else:
                st.success("Patrimônio localizado.")
                st.dataframe(ativo, use_container_width=True, hide_index=True)

    st.caption("Esta central é somente leitura. Registros e movimentações continuam sendo feitos nas telas próprias.")
