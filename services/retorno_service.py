import sqlite3
from pathlib import Path

DB_ASSISTENCIAS = Path("Banco Dados/assistencias.sqlite")


def _possui_assistencia_aberta(conn, patrimonio):
    if not DB_ASSISTENCIAS.exists():
        return False
    conn.execute("ATTACH DATABASE ? AS assistencias_db", (str(DB_ASSISTENCIAS.resolve()),))
    return conn.execute(
        "SELECT COUNT(*) FROM assistencias_db.assistencias WHERE patrimonio = ? AND lower(trim(status)) = lower(?)",
        (patrimonio, "Em assistência")
    ).fetchone()[0] > 0


def _normalizar_patrimonio(valor):
    valor = str(valor or "").strip()
    return valor[:-2] if valor.endswith(".0") else valor


def registrar_retorno(patrimonio, descricao, loja, chamado, nota_fiscal, data,
                      db_retorno="Banco Dados/retorno.sqlite",
                      db_cadastro="Banco Dados/cadastro_patrimonio.sqlite"):
    """Grava retorno e atualiza o cadastro na mesma transação SQLite."""
    patrimonio = _normalizar_patrimonio(patrimonio)
    descricao = str(descricao or "").strip()
    loja = str(loja or "").strip()
    if not patrimonio or not descricao or not loja:
        raise ValueError("Patrimônio, descrição e loja de origem são obrigatórios.")

    conn = sqlite3.connect(str(db_retorno), timeout=10)
    try:
        conn.execute("ATTACH DATABASE ? AS cadastro_db", (str(Path(db_cadastro).resolve()),))
        conn.execute("BEGIN IMMEDIATE")
        if patrimonio != "SEM PATRIMÔNIO":
            encontrados = conn.execute(
                "SELECT COUNT(*) FROM cadastro_db.cadastro_patrimonio "
                "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                (patrimonio,),
            ).fetchone()[0]
            if encontrados != 1:
                raise ValueError("Patrimônio não localizado de forma única no cadastro. Nenhum retorno foi salvo.")
            if _possui_assistencia_aberta(conn, patrimonio):
                raise ValueError("Patrimonio ja esta em assistencia aberta.")

        conn.execute(
            "INSERT INTO retorno (Patrimonio, Descricao, Loja, Chamado, Notafiscal, Data) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (patrimonio, descricao, loja, chamado, nota_fiscal, data.isoformat()),
        )
        if patrimonio != "SEM PATRIMÔNIO":
            conn.execute(
                "UPDATE cadastro_db.cadastro_patrimonio SET Portador = 'ESTOQUE TI', Filial = '1000' "
                "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                (patrimonio,),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
