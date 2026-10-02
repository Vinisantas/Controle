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


def _separar_termos(termo):
    """Aceita várias plaquetas separadas por linha, vírgula ou ponto e vírgula."""
    return [
        parte.strip()
        for parte in str(termo or "").replace(",", "\n").replace(";", "\n").splitlines()
        if parte.strip()
    ]


def _encontrar_coluna(colunas, aliases):
    mapa = {str(coluna).strip().casefold(): coluna for coluna in colunas}
    for alias in aliases:
        coluna = mapa.get(alias.strip().casefold())
        if coluna:
            return coluna
    return None


def _adicionar_idade(df):
    """Calcula a idade do patrimônio a partir da data de aquisição."""
    if df.empty:
        return df

    coluna_data = _encontrar_coluna(
        df.columns,
        ["Data Aquisição", "Data de Aquisição", "Data_Aquisicao", "Data Aquisicao", "Data Aquisição "],
    )
    if not coluna_data:
        df["Idade"] = "Não informada"
        return df

    datas = pd.to_datetime(df[coluna_data], errors="coerce", dayfirst=True)
    hoje = pd.Timestamp.now().normalize()

    def formatar_idade(data):
        if pd.isna(data) or data > hoje:
            return "Não informada"
        meses = max(0, (hoje.year - data.year) * 12 + hoje.month - data.month - (hoje.day < data.day))
        anos, meses_restantes = divmod(meses, 12)
        if anos and meses_restantes:
            return f"{anos} anos e {meses_restantes} meses"
        if anos:
            return f"{anos} anos"
        return f"{meses_restantes} meses"

    df["Idade"] = datas.map(formatar_idade)
    return df


def _buscar_cadastro(termo, filtro="Tudo"):
    if not os.path.exists(DB_CADASTRO):
        return pd.DataFrame()

    termos = _separar_termos(termo)
    if not termos:
        return pd.DataFrame()

    if filtro in {"Filial", "Fornecedor", "Portador"}:
        try:
            with sqlite3.connect(DB_CADASTRO) as conn:
                colunas = pd.read_sql_query("PRAGMA table_info(cadastro_patrimonio)", conn)["name"].tolist()
                aliases = {
                    "Filial": ["Filial"],
                    "Fornecedor": ["Fornecedor", "Fornec.", "Nome Fornecedor"],
                    "Portador": ["Portador"],
                }
                coluna = _encontrar_coluna(colunas, aliases[filtro])
                if not coluna:
                    return pd.DataFrame()
                identificador = '"' + str(coluna).replace('"', '""') + '"'
                encontrados = []
                for item in termos:
                    df_item = pd.read_sql_query(
                        f"SELECT * FROM cadastro_patrimonio WHERE CAST({identificador} AS TEXT) LIKE ? LIMIT 500",
                        conn,
                        params=(f"%{item}%",),
                    )
                    if not df_item.empty:
                        encontrados.append(df_item)
                if encontrados:
                    return pd.concat(encontrados, ignore_index=True).drop_duplicates()
        except Exception:
            return pd.DataFrame()

    numeros = [_normalizar(item) for item in termos]
    todos_sao_plaquetas = all(item.strip().isdigit() for item in termos)

    with sqlite3.connect(DB_CADASTRO) as conn:
        try:
            if todos_sao_plaquetas:
                valores = list(dict.fromkeys(int(numero) for numero in numeros))
                placeholders = ",".join("?" for _ in valores)
                df_exato = pd.read_sql_query(
                    f"SELECT * FROM cadastro_patrimonio WHERE CAST(Plaqueta AS INTEGER) IN ({placeholders})",
                    conn,
                    params=valores,
                )
                if not df_exato.empty:
                    return df_exato

            # Se nenhum patrimônio exato foi encontrado, preserva a busca por
            # texto/número em descrição, portador, filial e plaqueta.
            encontrados = []
            for item in termos:
                df_item = pd.read_sql_query(
                    "SELECT * FROM cadastro_patrimonio WHERE CAST(Plaqueta AS TEXT) LIKE ? OR [Desc. Bem] LIKE ? OR [Portador] LIKE ? OR CAST([Filial] AS TEXT) LIKE ? LIMIT 100",
                    conn,
                    params=(f"%{item}%", f"%{item}%", f"%{item}%", f"%{item}%"),
                )
                if not df_item.empty:
                    encontrados.append(df_item)
            if encontrados:
                return pd.concat(encontrados, ignore_index=True).drop_duplicates()
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def _buscar_movimentos(termo):
    resultados = []
    termos = _separar_termos(termo)
    numeros = {numero for numero in (_normalizar(item) for item in termos) if numero}
    for caminho, tipo in [(DB_SAIDA, "Saída"), (DB_RETORNO, "Retorno")]:
        if not os.path.exists(caminho):
            continue
        try:
            with sqlite3.connect(caminho) as conn:
                df = pd.read_sql_query("SELECT * FROM " + ("saida" if tipo == "Saída" else "retorno") + " ORDER BY id DESC LIMIT 1000", conn)
            if numeros and "Patrimonio" in df.columns and all(_normalizar(item) for item in termos):
                mask = df["Patrimonio"].astype(str).map(_normalizar).isin(numeros)
            else:
                texto = df.fillna("").astype(str).agg(" ".join, axis=1)
                mask = pd.Series(False, index=df.index)
                for item in termos:
                    mask |= texto.str.contains(item, case=False, na=False, regex=False)
            if mask.any():
                parte = df[mask].head(100).copy()
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
            df = pd.read_sql_query(f'SELECT * FROM "{tabela}" ORDER BY id DESC LIMIT 1000', conn)
        termos = _separar_termos(termo)
        numeros = {numero for numero in (_normalizar(item) for item in termos) if numero}
        coluna_patrimonio = next((c for c in df.columns if c.lower() == "patrimonio"), None)
        if numeros and coluna_patrimonio and all(_normalizar(item) for item in termos):
            return df[df[coluna_patrimonio].astype(str).map(_normalizar).isin(numeros)].head(100)
        texto = df.fillna("").astype(str).agg(" ".join, axis=1)
        mask = pd.Series(False, index=df.index)
        for item in termos:
            mask |= texto.str.contains(item, case=False, na=False, regex=False)
        return df[mask].head(100)
    except Exception:
        return pd.DataFrame()


def render_busca_universal():
    st.markdown("### 🔎 Busca universal")
    st.caption("Pesquise por patrimônio, filial, fornecedor ou portador.")

    with st.form("form_busca_universal", clear_on_submit=False):
        filtro = st.selectbox(
            "Filtrar por",
            ["Tudo", "Patrimônio", "Filial", "Fornecedor", "Portador"],
            key="busca_universal_filtro",
        )
        termo_digitado = st.text_area(
            "Patrimônios ou termos de busca",
            placeholder="Ex.:\n081840\n102021\n103031" if filtro == "Patrimônio" else "Digite o valor que deseja localizar...",
            height=110 if filtro == "Patrimônio" else 70,
            key="busca_universal_termo_multilinha",
            label_visibility="collapsed",
        )
        pesquisar = st.form_submit_button(
            "🔎 Pesquisar",
            type="primary",
            use_container_width=True,
        )

    if pesquisar:
        st.session_state["busca_universal_aplicada"] = termo_digitado.strip()
        st.session_state["busca_universal_filtro_aplicado"] = filtro
    termo = st.session_state.get("busca_universal_aplicada", "").strip()
    filtro_aplicado = st.session_state.get("busca_universal_filtro_aplicado", "Tudo")

    if not termo:
        st.caption("Digite uma ou mais plaquetas e clique em Pesquisar. Zeros à esquerda são aceitos.")
        return

    cadastro = _buscar_cadastro(termo, filtro_aplicado)
    termos = _separar_termos(termo)
    if filtro_aplicado == "Patrimônio":
        movimentos_lista = [_buscar_movimentos(item) for item in termos]
        movimentos_lista = [df for df in movimentos_lista if not df.empty]
        movimentos = pd.concat(movimentos_lista, ignore_index=True).drop_duplicates() if movimentos_lista else pd.DataFrame()
        assistencias_lista = [_buscar_assistencias(item) for item in termos]
        assistencias_lista = [df for df in assistencias_lista if not df.empty]
        assistencias = pd.concat(assistencias_lista, ignore_index=True).drop_duplicates() if assistencias_lista else pd.DataFrame()
    else:
        movimentos = pd.DataFrame()
        assistencias = pd.DataFrame()

    if cadastro.empty and movimentos.empty and assistencias.empty:
        st.warning(f"Nenhum registro encontrado para o filtro {filtro_aplicado}.")
        return

    if not cadastro.empty:
        cadastro = _adicionar_idade(cadastro)
        st.success(f"{len(cadastro)} patrimônio(s) encontrado(s).")
        st.markdown("#### 📋 Dados completos do patrimônio")
        st.dataframe(
            cadastro,
            hide_index=True,
            use_container_width=True,
            height=min(520, 100 + 42 * len(cadastro)),
        )

        if len(cadastro) == 1:
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
