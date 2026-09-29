

import sqlite3
from pathlib import Path

DB_SAIDA = Path("Banco Dados/saida.sqlite")
DB_CADASTRO = Path("Banco Dados/cadastro_patrimonio.sqlite")
DB_ASSISTENCIAS = Path("Banco Dados/assistencias.sqlite")
DESTINOS_VALIDOS = {"Loja / Filial", "Setor Interno", "Assistencia"}


def _normalizar_patrimonio(valor):
    valor = str(valor or "").strip()
    return valor[:-2] if valor.endswith(".0") else valor


def _possui_assistencia_aberta(conn, patrimonio):
    if not DB_ASSISTENCIAS.exists():
        return False
    conn.execute("ATTACH DATABASE ? AS assistencias_db", (str(DB_ASSISTENCIAS.resolve()),))
    return conn.execute(
        "SELECT COUNT(*) FROM assistencias_db.assistencias "
        "WHERE patrimonio = ? AND lower(trim(status)) LIKE 'em assist%'",
        (patrimonio,),
    ).fetchone()[0] > 0


def registrar_saida(dados):
    """Registra a saída e atualiza o cadastro na mesma transação SQLite."""
    patrimonio = _normalizar_patrimonio(dados.get("Patrimonio"))
    descricao = str(dados.get("Descricao") or "").strip()
    destinatario = str(dados.get("Destinatario") or "").strip()
    tipo_destino = str(dados.get("Tipo_Destino") or "").strip()
    usuario_setor = str(dados.get("Usuario_Setor") or "").strip()

    if not patrimonio:
        raise ValueError("Informe um patrimônio ou selecione explicitamente SEM PATRIMÔNIO.")
    if not descricao:
        raise ValueError("A descrição do equipamento é obrigatória.")
    if not destinatario:
        raise ValueError("O destinatário é obrigatório.")
    if tipo_destino not in DESTINOS_VALIDOS:
        raise ValueError("Tipo de destino inválido.")
    if tipo_destino == "Setor Interno" and not usuario_setor:
        raise ValueError("Informe o usuário responsável pelo setor interno.")

    conn = sqlite3.connect(str(DB_SAIDA), timeout=10)
    try:
        conn.execute("ATTACH DATABASE ? AS cadastro_db", (str(DB_CADASTRO.resolve()),))
        conn.execute("BEGIN IMMEDIATE")

        if patrimonio != "SEM PATRIMÔNIO":
            encontrados = conn.execute(
                "SELECT COUNT(*) FROM cadastro_db.cadastro_patrimonio "
                "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                (patrimonio,),
            ).fetchone()[0]
            if encontrados != 1:
                raise ValueError(
                    "Patrimônio não localizado de forma única no cadastro. "
                    "Confira a plaqueta; nenhum registro foi salvo."
                )
            portador = conn.execute(
                "SELECT COALESCE(Portador, '') FROM cadastro_db.cadastro_patrimonio "
                "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                (patrimonio,),
            ).fetchone()[0]
            if str(portador or "").strip().upper() == "SEM CONSERTO":
                raise ValueError(
                    "Este equipamento esta marcado como SEM CONSERTO e nao pode sair do estoque."
                )

            if _possui_assistencia_aberta(conn, patrimonio):
                raise ValueError("Patrimonio ja esta em assistencia aberta.")

        conn.execute(
            """INSERT INTO saida
            (Patrimonio, Descricao, Qtd, Motivo, Status_Equipamento,
             Tipo_Destino, Destinatario, Usuario_Setor, Chamado, Tecnico,
             Data, Observacao, Baixa_Senior)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                patrimonio, descricao, dados.get("Qtd", 1), dados.get("Motivo", ""),
                dados.get("Status_Equipamento", ""), tipo_destino, destinatario,
                usuario_setor, dados.get("Chamado", ""), dados.get("Tecnico", ""),
                dados["Data"].isoformat(), dados.get("Observacao", ""),
            ),
        )

        if patrimonio != "SEM PATRIMÔNIO":
            if tipo_destino == "Loja / Filial":
                conn.execute(
                    "UPDATE cadastro_db.cadastro_patrimonio SET Filial = ? "
                    "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                    (destinatario, patrimonio),
                )
            elif tipo_destino == "Setor Interno":
                conn.execute(
                    "UPDATE cadastro_db.cadastro_patrimonio SET Filial = ?, Portador = ? "
                    "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                    (destinatario, usuario_setor, patrimonio),
                )
            else:
                conn.execute(
                    "UPDATE cadastro_db.cadastro_patrimonio SET Portador = ?, Filial = '1000' "
                    "WHERE RTRIM(LTRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', ''))) = ?",
                    (destinatario, patrimonio),
                )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


