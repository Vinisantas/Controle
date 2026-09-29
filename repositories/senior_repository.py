"""Persistência SQLite do histórico bruto de importações Senior."""
import os
import sqlite3
from datetime import datetime
import pandas as pd

DB_SENIOR = "Banco Dados/senior_raw.sqlite"
DB_CADASTRO = "Banco Dados/cadastro_patrimonio.sqlite"


def obter_conexao_senior(db_senior=DB_SENIOR):
    os.makedirs(os.path.dirname(db_senior) or ".", exist_ok=True)
    return sqlite3.connect(db_senior)


def inicializar_banco_senior(db_senior=DB_SENIOR):
    with sqlite3.connect(db_senior) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS importacoes_senior (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_importacao TEXT NOT NULL,
            arquivo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            observacao TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS senior_geral (
            importacao_id INTEGER NOT NULL,
            Plaqueta TEXT NOT NULL,
            dados_json TEXT NOT NULL,
            FOREIGN KEY(importacao_id) REFERENCES importacoes_senior(id)
        )""")


def importar_snapshot(df, nome_arquivo, db_senior=DB_SENIOR):
    inicializar_banco_senior(db_senior)
    agora = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(db_senior) as conn:
        cursor = conn.execute(
            "INSERT INTO importacoes_senior (data_importacao, arquivo, quantidade) VALUES (?, ?, ?)",
            (agora, nome_arquivo, len(df))
        )
        importacao_id = cursor.lastrowid
        registros = [
            (importacao_id, str(linha["Plaqueta"]),
             linha.to_json(force_ascii=False, date_format="iso"))
            for _, linha in df.iterrows()
        ]
        conn.executemany(
            "INSERT INTO senior_geral (importacao_id, Plaqueta, dados_json) VALUES (?, ?, ?)",
            registros
        )
    return importacao_id


def carregar_plaquetas_cadastro(db_cadastro=DB_CADASTRO):
    if not os.path.exists(db_cadastro):
        return set()
    with sqlite3.connect(db_cadastro) as conn:
        df = pd.read_sql_query("SELECT Plaqueta FROM cadastro_patrimonio", conn)
    return set(df["Plaqueta"].astype(str).str.strip())


def adicionar_novos_patrimonios(df, db_cadastro=DB_CADASTRO):
    """Insere apenas plaquetas ausentes; nunca atualiza ou exclui existentes."""
    if df.empty:
        return 0
    if not os.path.exists(db_cadastro):
        raise FileNotFoundError(f"Banco de cadastro não encontrado: {db_cadastro}")
    with sqlite3.connect(db_cadastro, timeout=10) as conn:
        existentes = carregar_plaquetas_cadastro(db_cadastro)
        novos = df[~df["Plaqueta"].isin(existentes)].copy()
        if novos.empty:
            return 0
        colunas_banco = [
            linha[1] for linha in conn.execute("PRAGMA table_info(cadastro_patrimonio)").fetchall()
        ]
        dados = []
        for _, linha in novos.iterrows():
            registro = {col: None for col in colunas_banco}
            for col in colunas_banco:
                if col in linha.index:
                    registro[col] = linha[col]
            dados.append(registro)
        colunas = [c for c in colunas_banco if any(d.get(c) is not None for d in dados)]
        if not colunas:
            raise ValueError("Nenhuma coluna compatível para inserir os novos patrimônios.")
        placeholders = ", ".join(["?"] * len(colunas))
        colunas_sql = ", ".join('"' + c.replace('"', '""') + '"' for c in colunas)
        sql = f"INSERT INTO cadastro_patrimonio ({colunas_sql}) VALUES ({placeholders})"
        conn.executemany(sql, [[registro[c] for c in colunas] for registro in dados])
        return len(dados)


def carregar_importacoes(db_senior=DB_SENIOR):
    inicializar_banco_senior(db_senior)
    with sqlite3.connect(db_senior) as conn:
        return pd.read_sql_query(
            "SELECT * FROM importacoes_senior ORDER BY id DESC", conn
        )
