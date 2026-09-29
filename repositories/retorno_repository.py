"""Persistência SQLite dos retornos de equipamentos.

Este módulo concentra consultas e gravações do histórico de retornos.
"""
import os
import sqlite3
import pandas as pd

DB_NAME = "Banco Dados/retorno.sqlite"
DB_CADASTRO = "Banco Dados/cadastro_patrimonio.sqlite"


def inicializar_banco(db_name=DB_NAME):
    os.makedirs(os.path.dirname(db_name) or ".", exist_ok=True)
    with sqlite3.connect(db_name) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS retorno (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Patrimonio TEXT,
                Descricao TEXT,
                Loja TEXT,
                Chamado TEXT,
                Notafiscal TEXT,
                Data DATE
            )
        """)


def carregar_dados(db_name=DB_NAME):
    with sqlite3.connect(db_name) as conn:
        return pd.read_sql_query(
            "SELECT * FROM retorno ORDER BY Data DESC",
            conn,
            parse_dates=["Data"],
        )


def buscar_dados_patrimonio(codigo, db_cadastro=DB_CADASTRO):
    """Busca descrição e loja sugerida sem carregar o cadastro inteiro na UI."""
    if not codigo or not os.path.exists(db_cadastro):
        return None
    with sqlite3.connect(db_cadastro) as conn:
        tabelas = [
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        for tabela in tabelas:
            # Nome da tabela vem do catálogo SQLite e é delimitado como identificador.
            nome_seguro = tabela.replace('"', '""')
            colunas = [
                row[1] for row in conn.execute(f'PRAGMA table_info("{nome_seguro}")')
            ]
            mapa = {c.strip().lower(): c for c in colunas}
            chave = mapa.get("plaqueta") or mapa.get("patrimonio")
            descricao = mapa.get("desc. bem") or mapa.get("descricao") or mapa.get("nome")
            if not chave or not descricao:
                continue
            chave_sql = chave.replace('"', '""')
            desc_sql = descricao.replace('"', '""')
            loja = next((mapa[k] for k in ("loja", "filial", "unidade") if k in mapa), None)
            loja_sql = f', "{loja.replace(chr(34), chr(34)*2)}"' if loja else ""
            row = conn.execute(
                f'SELECT "{desc_sql}"{loja_sql} FROM "{nome_seguro}" '
                f'WHERE TRIM(REPLACE(CAST("{chave_sql}" AS TEXT), ".0", "")) = ? LIMIT 1',
                (str(codigo).strip(),),
            ).fetchone()
            if row:
                valor_loja = row[1] if len(row) > 1 else ""
                if valor_loja is not None and str(valor_loja).endswith(".0"):
                    try:
                        valor_loja = str(int(float(valor_loja)))
                    except (ValueError, TypeError):
                        pass
                return {"descricao": str(row[0] or "").strip(), "loja": str(valor_loja or "").strip()}
    return None


def atualizar_linha(id_registro, coluna, novo_valor, db_name=DB_NAME):
    colunas_permitidas = {"Patrimonio", "Descricao", "Loja", "Chamado", "Notafiscal", "Data"}
    if coluna not in colunas_permitidas:
        raise ValueError("Coluna não permitida para atualização.")
    with sqlite3.connect(db_name) as conn:
        conn.execute(f'UPDATE retorno SET "{coluna}" = ? WHERE id = ?', (novo_valor, id_registro))


def excluir_linha(id_registro, db_name=DB_NAME):
    with sqlite3.connect(db_name) as conn:
        conn.execute("DELETE FROM retorno WHERE id = ?", (id_registro,))
