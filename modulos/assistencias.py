import pandas as pd
import streamlit as st

from services.assistencia_service import calcular_indicadores

from repositories.assistencia_repository import inicializar_banco, carregar_assistencias, registrar_assistencia, atualizar_assistencia, excluir_assistencia, buscar_historico_patrimonio
from services.assistencia_service import calcular_indicadores


def render_assistencias():
    inicializar_banco()

    st.markdown("""
        <style>
        .assistencia-card {
            background: var(--secondary-background-color);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--primary-color);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🛠️ Assistências Técnicas")
    st.caption("Controle de consertos, custos e histórico por equipamento.")
    st.divider()

    df = carregar_assistencias()
    indicadores = calcular_indicadores(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Assistências", indicadores["total"])
    col2.metric("Gasto acumulado", f"R$ {indicadores['gasto_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("Gasto neste mês", f"R$ {indicadores['gasto_mes']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col4.metric("Em assistência", indicadores["abertas"])

    st.markdown("### ➕ Registrar conserto")
    with st.expander("Nova assistência", expanded=True):
        with st.form("formulario_assistencia"):
            c1, c2, c3 = st.columns(3)
            patrimonio = c1.text_input("Patrimônio *")
            descricao = c2.text_input("Descrição")
            fornecedor = c3.text_input("Assistência / Fornecedor")

            c4, c5, c6 = st.columns(3)
            chamado = c4.text_input("Chamado")
            nota_fiscal = c5.text_input("Nota fiscal")
            status = c6.selectbox(
                "Status", ["Em assistência", "Concluída", "Sem conserto", "Cancelada"]
            )

            defeito = st.text_area("Defeito apresentado")
            servico = st.text_area("Serviço realizado")
            c7, c8, c9 = st.columns(3)
            data_entrada = c7.date_input("Entrada")
            data_saida = c8.date_input("Saída")
            valor_pago = c9.number_input("Valor pago (R$)", min_value=0.0, step=10.0)

            observacao = st.text_area("Observação")
            salvar = st.form_submit_button("💾 Registrar assistência", type="primary")

            if salvar:
                if not patrimonio.strip():
                    st.error("Informe o patrimônio do equipamento.")
                else:
                    registrar_assistencia({
                        "patrimonio": patrimonio.strip(),
                        "descricao": descricao.strip(),
                        "fornecedor": fornecedor.strip(),
                        "chamado": chamado.strip(),
                        "nota_fiscal": nota_fiscal.strip(),
                        "defeito": defeito.strip(),
                        "servico": servico.strip(),
                        "status": status,
                        "data_entrada": data_entrada.isoformat(),
                        "data_saida": data_saida.isoformat(),
                        "valor_pago": float(valor_pago),
                        "observacao": observacao.strip()
                    })
                    st.success("Assistência registrada.")
                    st.rerun()

    st.markdown("### 📊 Gastos por período")
    if not df.empty:
        df_gastos = df.copy()
        df_gastos["mes"] = pd.to_datetime(df_gastos["data_entrada"]).dt.to_period("M").astype(str)
        gastos_mensais = df_gastos.groupby("mes", as_index=False)["valor_pago"].sum()
        gastos_mensais = gastos_mensais.rename(columns={"valor_pago": "Valor pago"})
        st.bar_chart(gastos_mensais.set_index("mes"))

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 🏢 Gasto por assistência")
            por_fornecedor = df.groupby("fornecedor", as_index=False)["valor_pago"].sum()
            por_fornecedor = por_fornecedor.sort_values("valor_pago", ascending=False)
            st.dataframe(por_fornecedor, hide_index=True, use_container_width=True)
        with col_b:
            st.markdown("#### 🖥️ Equipamentos com maior custo")
            por_patrimonio = df.groupby(
                ["patrimonio", "descricao"], as_index=False
            )["valor_pago"].agg(["sum", "count"]).reset_index()
            por_patrimonio = por_patrimonio.rename(
                columns={"sum": "Gasto total", "count": "Qtde assistências"}
            ).sort_values("Gasto total", ascending=False)
            st.dataframe(por_patrimonio, hide_index=True, use_container_width=True)

    st.markdown("### 🔎 Histórico de assistências")
    if df.empty:
        st.info("Nenhuma assistência registrada ainda.")
        return

    filtro = st.text_input(
        "Pesquisar equipamento, fornecedor ou chamado",
        placeholder="Ex.: patrimônio 12345, Dell, #45091"
    )
    exibicao = df.copy()
    if filtro:
        texto = exibicao.fillna("").astype(str).agg(" ".join, axis=1)
        exibicao = exibicao[texto.str.contains(filtro, case=False, na=False)]

    colunas = [
        "id", "patrimonio", "descricao", "fornecedor", "chamado",
        "status", "data_entrada", "data_saida", "valor_pago"
    ]
    st.dataframe(
        exibicao[colunas],
        hide_index=True,
        use_container_width=True,
        column_config={
            "id": None,
            "valor_pago": st.column_config.NumberColumn("Valor pago", format="R$ %.2f"),
            "data_entrada": st.column_config.DateColumn("Entrada", format="DD/MM/YYYY"),
            "data_saida": st.column_config.DateColumn("Saída", format="DD/MM/YYYY")
        }
    )

    st.markdown("### ✏️ Atualizar assistência")
    opcoes_edicao = exibicao[
        ["id", "patrimonio", "descricao", "fornecedor", "chamado", "status",
         "data_entrada", "data_saida", "valor_pago"]
    ].copy()
    opcoes_edicao["rotulo"] = opcoes_edicao.apply(
        lambda r: f"#{int(r['id'])} · {r['patrimonio']} · {r['status']}",
        axis=1
    )
    if not opcoes_edicao.empty:
        selecionado_edicao = st.selectbox(
            "Selecionar assistência para atualizar",
            [""] + opcoes_edicao["rotulo"].tolist()
        )
        if selecionado_edicao:
            registro_edicao = opcoes_edicao[
                opcoes_edicao["rotulo"] == selecionado_edicao
            ].iloc[0]
            e1, e2, e3 = st.columns(3)
            novo_fornecedor = e1.text_input(
                "Assistência / Fornecedor",
                value=str(registro_edicao["fornecedor"] or ""),
                key="editar_fornecedor"
            )
            novo_chamado = e2.text_input(
                "Chamado",
                value=str(registro_edicao["chamado"] or ""),
                key="editar_chamado"
            )
            status_opcoes = ["Em assistência", "Concluída", "Sem conserto", "Cancelada"]
            status_atual = str(registro_edicao["status"] or "")
            novo_status = e3.selectbox(
                "Status",
                status_opcoes,
                index=status_opcoes.index(status_atual)
                if status_atual in status_opcoes else 0,
                key="editar_status"
            )
            e4, e5 = st.columns(2)
            valor_atual = float(registro_edicao["valor_pago"] or 0)
            nova_data_saida = e4.date_input(
                "Saída",
                value=pd.to_datetime(registro_edicao["data_saida"]).date()
                if pd.notna(registro_edicao["data_saida"])
                else pd.Timestamp.today().date(),
                key="editar_data_saida"
            )
            novo_valor = e5.number_input(
                "Valor pago (R$)",
                min_value=0.0,
                value=valor_atual,
                step=10.0,
                key="editar_valor"
            )
            salvar_edicao = st.button(
                "💾 Salvar atualização",
                type="primary",
                key="salvar_edicao_assistencia"
            )
            if salvar_edicao:
                try:
                    id_edicao = int(registro_edicao["id"])
                    atualizar_assistencia(id_edicao, "fornecedor", novo_fornecedor.strip())
                    atualizar_assistencia(id_edicao, "chamado", novo_chamado.strip())
                    atualizar_assistencia(id_edicao, "status", novo_status)
                    atualizar_assistencia(
                        id_edicao, "data_saida", nova_data_saida.isoformat()
                    )
                    atualizar_assistencia(id_edicao, "valor_pago", float(novo_valor))
                    st.success("Assistência atualizada e cadastro sincronizado.")
                    st.rerun()
                except (ValueError, TypeError) as exc:
                    st.error(str(exc))

    st.markdown("### 🗑️ Corrigir lançamento")
    opcoes_exclusao = exibicao[["id", "patrimonio", "descricao", "status", "valor_pago"]].copy()
    opcoes_exclusao["rotulo"] = opcoes_exclusao.apply(
        lambda r: f"#{int(r['id'])} · {r['patrimonio']} · {r['status']} · R$ {float(r['valor_pago']):.2f}",
        axis=1
    )
    if not opcoes_exclusao.empty:
        selecionado_exclusao = st.selectbox(
            "Selecionar lançamento para exclusão",
            [""] + opcoes_exclusao["rotulo"].tolist()
        )
        confirmar_exclusao = st.checkbox(
            "Confirmo que este lançamento foi registrado por engano e não deve permanecer no histórico."
        )
        if selecionado_exclusao and confirmar_exclusao:
            registro = opcoes_exclusao[
                opcoes_exclusao["rotulo"] == selecionado_exclusao
            ].iloc[0]
            if st.button("🗑️ Excluir lançamento", type="secondary"):
                try:
                    excluir_assistencia(int(registro["id"]))
                    st.success("Lançamento excluído e removido dos indicadores.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

    patrimonio_selecionado = st.selectbox(
        "Ver histórico completo do patrimônio",
        [""] + sorted(exibicao["patrimonio"].dropna().astype(str).unique().tolist())
    )
    if patrimonio_selecionado:
        historico = df[df["patrimonio"].astype(str) == patrimonio_selecionado]
        total = historico["valor_pago"].sum()
        st.info(
            f"Este equipamento possui {len(historico)} assistência(s), "
            f"com gasto acumulado de R$ {total:,.2f}."
        )
        st.dataframe(
            historico[
                ["data_entrada", "data_saida", "fornecedor", "defeito",
                 "servico", "status", "valor_pago", "chamado"]
            ],
            hide_index=True,
            use_container_width=True
        )

