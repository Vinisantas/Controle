import pandas as pd
import streamlit as st

from repositories.senior_repository import inicializar_banco_senior, importar_snapshot, adicionar_novos_patrimonios, carregar_importacoes
from services.senior_service import preparar_excel, comparar_com_cadastro


def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_importacao_senior():
    inicializar_banco_senior()
    st.markdown("""<style>
    .importacao-card {background:var(--secondary-background-color); border:1px solid var(--border-color); border-left:4px solid var(--primary-color); border-radius:10px; padding:14px 16px; margin-bottom:12px;}
    </style>""", unsafe_allow_html=True)
    st.title("📥 Importação Senior")
    st.caption("O relatório baixado do Senior é guardado como fonte bruta e não sobrescreve o histórico do TI Controle.")
    st.divider()
    st.info("Fluxo seguro: Senior → GERAL/RAW → comparação → adicionar somente os novos. Registros existentes no TI Controle não são alterados nem excluídos.")

    arquivo = st.file_uploader("Selecione o Excel exportado do Senior", type=["xlsx", "xls"])
    if arquivo is not None:
        try:
            df = preparar_excel(arquivo)
            novas, existentes, removidos = comparar_com_cadastro(df)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Registros no Senior", f"{len(df):,}")
            c2.metric("Novos patrimônios", f"{len(novas):,}")
            c3.metric("Já existentes", f"{len(existentes):,}")
            c4.metric("Não vieram no Senior", f"{len(removidos):,}")
            st.markdown("### 🔎 Prévia do relatório")
            st.dataframe(df.head(30), use_container_width=True, hide_index=True)
            st.warning("Atenção: 'não veio no Senior' não significa baixa. O registro é preservado e não será excluído automaticamente.")
            if len(novas) > 0:
                st.markdown("### ➕ Novos patrimônios para o TI Controle")
                st.caption("Somente as plaquetas que ainda não existem no cadastro serão incluídas. Registros já existentes permanecem intactos.")
                st.dataframe(novas.head(30), use_container_width=True, hide_index=True)
                confirmar = st.checkbox("Confirmo que quero adicionar somente os novos patrimônios", key="confirmar_novos_senior")
            else:
                confirmar = False
                st.success("Nenhum patrimônio novo encontrado. O cadastro do TI Controle não precisa ser alterado.")

            c1, c2 = st.columns(2)
            with c1:
                guardar = st.button("💾 Guardar GERAL / RAW", use_container_width=True)
            with c2:
                adicionar = st.button("➕ Adicionar novos ao TI Controle", type="primary", use_container_width=True, disabled=not confirmar)

            if guardar or adicionar:
                id_importacao = importar_snapshot(df, arquivo.name)
                adicionados = adicionar_novos_patrimonios(novas) if adicionar else 0
                st.success(f"Importação #{id_importacao} armazenada. {adicionados} novo(s) patrimônio(s) adicionado(s) ao TI Controle. Nenhum registro existente foi alterado ou excluído.")
                st.rerun()
        except Exception as erro:
            st.error(f"Não foi possível ler o relatório: {erro}")

    st.markdown("### 🕒 Histórico de importações")
    historico = carregar_importacoes()
    if historico.empty:
        st.info("Nenhuma importação do Senior registrada ainda.")
    else:
        st.dataframe(historico, use_container_width=True, hide_index=True)
