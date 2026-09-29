import os
import sqlite3
import pandas as pd
import streamlit as st

from repositories import patrimonio_repository

DB_CADASTRO = "Banco Dados/cadastro_patrimonio.sqlite"
DB_SAIDA = "Banco Dados/saida.sqlite"
DB_RETORNO = "Banco Dados/retorno.sqlite"
DB_ASSISTENCIA = "Banco Dados/assistencias.sqlite"


def _normalizar(valor):
    return "".join(ch for ch in str(valor or "").strip() if ch.isdigit())


def _buscar_cadastro(termo):
    if not os.path.exists(DB_CADASTRO):
        return pd.DataFrame()
    numero = _normalizar(termo)
    with sqlite3.connect(DB_CADASTRO) as conn:
        try:
            if numero:
                df = pd.read_sql_query(
                    "SELECT * FROM cadastro_patrimonio WHERE CAST(Plaqueta AS INTEGER) = ? LIMIT 20",
                    conn, params=(int(numero),)
                )
            else:
                df = pd.DataFrame()
            if df.empty:
                df = pd.read_sql_query(
                    "SELECT * FROM cadastro_patrimonio WHERE [Desc. Bem] LIKE ? OR [Portador] LIKE ? OR CAST([Filial] AS TEXT) LIKE ? LIMIT 20",
                    conn, params=(f"%{termo}%", f"%{termo}%", f"%{termo}%")
                )
        except Exception:
            return pd.DataFrame()
    return df


def _buscar_movimentos(termo):
    resultados = []
    numero = _normalizar(termo)
    for caminho, tipo in [(DB_SAIDA, "Saída"), (DB_RETORNO, "Retorno")]:
        if not os.path.exists(caminho):
            continue
        try:
            with sqlite3.connect(caminho) as conn:
                df = pd.read_sql_query("SELECT * FROM " + ("saida" if tipo == "Saída" else "retorno") + " ORDER BY id DESC LIMIT 300", conn)
            if numero and "Patrimonio" in df.columns:
                mask = df["Patrimonio"].astype(str).map(_normalizar) == numero
            else:
                texto = df.fillna("").astype(str).agg(" ".join, axis=1)
                mask = texto.str.contains(str(termo), case=False, na=False)
            if mask.any():
                parte = df[mask].head(10).copy()
                parte.insert(0, "Tipo", tipo)
                resultados.append(parte)
        except Exception:
            continue
    return pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame()


def _buscar_assistencias(termo):
    if not os.path.exists(DB_ASSISTENCIA):
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_ASSISTENCIA) as conn:
            tabelas = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            tabela = next((t for t in tabelas if t.lower() in {"assistencias", "assistencia"}), None)
            if not tabela:
                return pd.DataFrame()
            df = pd.read_sql_query(f'SELECT * FROM "{tabela}" ORDER BY id DESC LIMIT 300', conn)
        numero = _normalizar(termo)
        if numero and "patrimonio" in df.columns:
            return df[df["patrimonio"].astype(str).map(_normalizar) == numero].head(10)
        texto = df.fillna("").astype(str).agg(" ".join, axis=1)
        return df[texto.str.contains(str(termo), case=False, na=False)].head(10)
    except Exception:
        return pd.DataFrame()
def render_busca_universal():
    st.markdown("### 🔎 Busca universal")
    st.caption("Uma busca para encontrar o equipamento e o que aconteceu com ele, sem precisar abrir várias telas.")

    termo = st.text_input(
        "Pesquisar",
        placeholder="Patrimônio, descrição, loja, portador, chamado...",
        key="busca_universal_termo",
        label_visibility="collapsed",
    ).strip()

    if not termo:
        st.caption("Digite uma plaqueta para começar. Leitores com zeros à esquerda também são aceitos.")
        return

    cadastro = _buscar_cadastro(termo)
    movimentos = _buscar_movimentos(termo)
    assistencias = _buscar_assistencias(termo)

    if cadastro.empty and movimentos.empty and assistencias.empty:
        st.warning("Nenhum registro encontrado para essa busca.")
        return

    if not cadastro.empty:
        ativo = cadastro.iloc[0]
        plaqueta = str(ativo.get("Plaqueta", "")).replace(".0", "")
        descricao = str(ativo.get("Desc. Bem", "Não informado"))
        filial = str(ativo.get("Filial", "Não informado"))
        portador = str(ativo.get("Portador", "Não informado"))
        local = str(ativo.get("Desc. Local", ""))

        st.markdown(f"**{plaqueta.zfill(6)} · {descricao}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Local / Filial", filial)
        c2.metric("Portador", portador)
        c3.metric("Localização", local or "Não informada")

        a1, a2, a3, a4 = st.columns(4)
        if a1.button("📤 Enviar", key="busca_enviar", use_container_width=True):
            st.session_state["txt_patrimonio"] = plaqueta
            st.session_state["menu_atual"] = "➡️ Saída Equipamentos"
            st.rerun()
        if a2.button("📥 Receber", key="busca_receber", use_container_width=True):
            st.session_state["txt_patrimonio"] = plaqueta
            st.session_state["menu_atual"] = "↩️ Retorno Equipamentos"
            st.rerun()
        if a3.button("🔧 Assistência", key="busca_assistencia", use_container_width=True):
            st.session_state["assistencia_patrimonio"] = plaqueta
            st.session_state["menu_atual"] = "🛠️ Assistências"
            st.rerun()
        if a4.button("🕒 Histórico", key="busca_historico", use_container_width=True):
            st.session_state["historico_patrimonio_busca"] = plaqueta
            st.session_state["menu_atual"] = "🕒 Histórico Geral"
            st.rerun()

    if not movimentos.empty:
        st.markdown("#### 🕒 Movimentações encontradas")
        colunas = [c for c in ["Tipo", "Patrimonio", "Descricao", "Destinatario", "Loja", "Chamado", "Tecnico", "Data", "Motivo"] if c in movimentos.columns]
        st.dataframe(movimentos[colunas], hide_index=True, use_container_width=True)

    if not assistencias.empty:
        st.markdown("#### 🔧 Assistências encontradas")
        colunas = [c for c in ["id", "patrimonio", "descricao", "fornecedor", "chamado", "status", "data_entrada", "data_saida", "valor_pago"] if c in assistencias.columns]
        st.dataframe(assistencias[colunas], hide_index=True, use_container_width=True)
