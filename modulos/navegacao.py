"""Despacho central das páginas da Gestão de Ativos."""

import streamlit as st

from modulos.consulta_patrimonio import render_patrimonio, carregar_dataFrameBaixas
from modulos.Histórico_Geral import render_historico
from modulos.SaídaEquipamentos import render_saidas
from modulos.RetornoEquipamentos import render_retornos
from modulos.assistente_ti import render_assistente_ti
from modulos.assistencias import render_assistencias
from modulos.importacao_senior import render_importacao_senior
from dashboards.estoque import render_estoque
from dashboards.suporte import render_sup
from dashboards.central import render_central_dashboards


def _renderizar_baixados():
    """Mostra a consulta de patrimônios baixados."""
    st.title("Consulta Baixados")
    st.caption("Ativos desativados e baixados do inventário")
    st.divider()

    df = carregar_dataFrameBaixas()
    if df.empty:
        st.warning("Banco de Baixados não disponível ou vazio.")
        return

    st.markdown("### 🔎 Consulta de Baixados")
    filtro = st.text_input("Consultar Plaqueta ou Descrição").strip().upper()

    if filtro:
        plaqueta = df["Plaqueta"].astype(str)
        descricao = df["Desc. Bem"].astype(str)
        df = df[
            plaqueta.str.contains(filtro, case=False, na=False)
            | descricao.str.contains(filtro, case=False, na=False)
        ]

    st.dataframe(df, use_container_width=True, hide_index=True)


def _abrir_pagina(pagina):
    """Navega para uma página operacional sem alterar dados."""
    st.session_state["menu_atual"] = pagina


def _renderizar_visao_geral():
    """Página inicial com atalhos; não consulta nem grava bancos."""
    st.title("Visão Geral")
    st.caption("Central de operação da Gestão de Ativos TI")
    st.divider()
    st.write("Acesse rapidamente as tarefas do dia a dia. Os registros patrimoniais continuam sendo feitos nas telas próprias.")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("🔎 Patrimônio")
            st.caption("Localize equipamentos e consulte seus dados.")
            st.button("Consultar patrimônio", use_container_width=True, on_click=_abrir_pagina, args=("🔍 Consulta Patrimônio",))
    with col2:
        with st.container(border=True):
            st.subheader("➡️ Movimentações")
            st.caption("Registre saídas e retornos de equipamentos.")
            st.button("Registrar saída", use_container_width=True, on_click=_abrir_pagina, args=("➡️ Saída Equipamentos",))
            st.button("Registrar retorno", use_container_width=True, on_click=_abrir_pagina, args=("↩️ Retorno Equipamentos",))
    with col3:
        with st.container(border=True):
            st.subheader("📊 Acompanhamento")
            st.caption("Consulte estoque, suporte e histórico.")
            st.button("Dashboard de estoque", use_container_width=True, on_click=_abrir_pagina, args=("📊 Dashboard Estoque",))
            st.button("Histórico geral", use_container_width=True, on_click=_abrir_pagina, args=("🕒 Histórico Geral",))

    st.info("O BI analítico é consumido no Power BI. Esta aplicação não se conecta ao PostgreSQL; o banco analítico é acessado separadamente pelo IP da máquina Linux.")


def renderizar_pagina(opcao):
    """Renderiza a página selecionada no menu principal."""
    paginas = {
        "➡️ Saída Equipamentos": render_saidas,
        "↩️ Retorno Equipamentos": render_retornos,
        "🕒 Histórico Geral": render_historico,
        "📊 Central de Dashboards": render_central_dashboards,
        "📊 Dashboard Estoque": render_estoque,
        "📈 Dashboard Sup": render_sup,
        "🤖 Assistente de TI": render_assistente_ti,
        "🛠️ Assistências": render_assistencias,
        "📥 Importação Senior": render_importacao_senior,
    }

    if opcao == "🏠 Visão Geral":
        _renderizar_visao_geral()
    elif opcao == "🔍 Consulta Patrimônio":
        st.title("Consulta Patrimônio")
        st.caption("Gerencie e rastreie os ativos de TI em tempo real")
        st.divider()
        render_patrimonio()
    elif opcao == "🗑️ Saídas (Histórico)":
        _renderizar_baixados()
    elif opcao in paginas:
        paginas[opcao]()
    else:
        st.warning("Página não encontrada. Selecione uma opção no menu.")
