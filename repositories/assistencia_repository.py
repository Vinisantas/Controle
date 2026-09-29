"""Persistência e sincronização SQLite das assistências técnicas."""
import os
import sqlite3
import pandas as pd

DB_ASSISTENCIAS = "Banco Dados/assistencias.sqlite"
DB_CADASTRO = "Banco Dados/cadastro_patrimonio.sqlite"


def obter_conexao(db_assistencias=DB_ASSISTENCIAS):
    os.makedirs(os.path.dirname(db_assistencias) or ".", exist_ok=True)
    return sqlite3.connect(db_assistencias, timeout=10)


def inicializar_banco(db_assistencias=DB_ASSISTENCIAS):
    with obter_conexao(db_assistencias) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patrimonio TEXT NOT NULL,
                descricao TEXT,
                fornecedor TEXT,
                chamado TEXT,
                nota_fiscal TEXT,
                defeito TEXT,
                servico TEXT,
                status TEXT NOT NULL DEFAULT 'Em assistência',
                data_entrada DATE NOT NULL,
                data_saida DATE,
                valor_pago REAL NOT NULL DEFAULT 0,
                observacao TEXT
            )
        """)


def carregar_assistencias(db_assistencias=DB_ASSISTENCIAS):
    inicializar_banco(db_assistencias)
    with obter_conexao(db_assistencias) as conn:
        return pd.read_sql_query(
            "SELECT * FROM assistencias ORDER BY data_entrada DESC, id DESC",
            conn, parse_dates=["data_entrada", "data_saida"]
        )


def _normalizar_patrimonio(patrimonio):
    valor = str(patrimonio or "").strip()
    return valor[:-2] if valor.endswith(".0") else valor


def _sincronizar_cadastro(conn, patrimonio, status, fornecedor="", db_cadastro=DB_CADASTRO):
    patrimonio = _normalizar_patrimonio(patrimonio)
    if not patrimonio or patrimonio.upper() == "SEM PATRIMÔNIO":
        return
    if not os.path.exists(db_cadastro):
        raise FileNotFoundError(f"Banco de cadastro não encontrado: {db_cadastro}")

    conn.execute("ATTACH DATABASE ? AS cadastro_db", (os.path.abspath(db_cadastro),))
    quantidade = conn.execute(
        'SELECT COUNT(*) FROM cadastro_db.cadastro_patrimonio WHERE "Plaqueta" = ?',
        (patrimonio,)
    ).fetchone()[0]
    if quantidade != 1:
        raise ValueError("Patrimônio não encontrado ou duplicado no cadastro.")

    status_normalizado = str(status or "").strip().lower()
    if status_normalizado.startswith(("conclu", "cancel")):
        portador = "ESTOQUE TI"
    elif status_normalizado.startswith("sem conserto"):
        portador = "SEM CONSERTO"
    else:
        portador = str(fornecedor or "").strip() or "ASSISTÊNCIA"

    conn.execute(
        'UPDATE cadastro_db.cadastro_patrimonio SET "Filial" = ?, "Portador" = ? WHERE "Plaqueta" = ?',
        ("1000", portador, patrimonio)
    )


def registrar_assistencia(dados, db_assistencias=DB_ASSISTENCIAS, db_cadastro=DB_CADASTRO):
    inicializar_banco(db_assistencias)
    conn = obter_conexao(db_assistencias)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("""
            INSERT INTO assistencias (
                patrimonio, descricao, fornecedor, chamado, nota_fiscal,
                defeito, servico, status, data_entrada, data_saida,
                valor_pago, observacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["patrimonio"], dados["descricao"], dados["fornecedor"],
            dados["chamado"], dados["nota_fiscal"], dados["defeito"],
            dados["servico"], dados["status"], dados["data_entrada"],
            dados["data_saida"], dados["valor_pago"], dados["observacao"]
        ))
        _sincronizar_cadastro(conn, dados["patrimonio"], dados["status"],
                              dados["fornecedor"], db_cadastro)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def atualizar_assistencia(id_registro, coluna, valor, db_assistencias=DB_ASSISTENCIAS,
                          db_cadastro=DB_CADASTRO):
    permitidas = {"fornecedor", "chamado", "nota_fiscal", "defeito", "servico",
                  "status", "data_entrada", "data_saida", "valor_pago", "observacao"}
    if coluna not in permitidas:
        raise ValueError("Campo não permitido para atualização.")
    conn = obter_conexao(db_assistencias)
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute(f"UPDATE assistencias SET {coluna} = ? WHERE id = ?",
                           (valor, id_registro))
        if cur.rowcount != 1:
            raise ValueError("Assistência não encontrada.")
        registro = conn.execute(
            "SELECT patrimonio, status, fornecedor FROM assistencias WHERE id = ?",
            (id_registro,)
        ).fetchone()
        _sincronizar_cadastro(conn, registro[0], registro[1], registro[2], db_cadastro)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_assistencia(id_registro, db_assistencias=DB_ASSISTENCIAS, db_cadastro=DB_CADASTRO):
    try:
        id_registro = int(id_registro)
    except (TypeError, ValueError):
        raise ValueError("ID de assistência inválido.")
    conn = obter_conexao(db_assistencias)
    try:
        conn.execute("BEGIN IMMEDIATE")
        registro = conn.execute("SELECT patrimonio FROM assistencias WHERE id = ?",
                                (id_registro,)).fetchone()
        if registro is None:
            raise ValueError("Assistência não encontrada.")
        cur = conn.execute("DELETE FROM assistencias WHERE id = ?", (id_registro,))
        if cur.rowcount != 1:
            raise ValueError("Assistência não encontrada.")
        _sincronizar_cadastro(conn, registro[0], "Cancelada", db_cadastro=db_cadastro)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def buscar_historico_patrimonio(patrimonio, db_assistencias=DB_ASSISTENCIAS):
    df = carregar_assistencias(db_assistencias)
    if df.empty:
        return df
    return df[df["patrimonio"].astype(str) == str(patrimonio)].copy()
