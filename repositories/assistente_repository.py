"""Leituras centralizadas dos bancos usados pelo Assistente de TI."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "Banco Dados"
PATRIMONIO_DB = DB_DIR / "cadastro_patrimonio.sqlite"
SAIDA_DB = DB_DIR / "saida.sqlite"
RETORNO_DB = DB_DIR / "retorno.sqlite"
ESTOQUE_DB = DB_DIR / "estoque.sqlite"


def _read_dataframe(database: Path, query: str, params: tuple = ()) -> pd.DataFrame:
    if not database.exists():
        return pd.DataFrame()

    with sqlite3.connect(database) as connection:
        return pd.read_sql_query(query, connection, params=params)


def carregar_ativos() -> pd.DataFrame:
    return _read_dataframe(PATRIMONIO_DB, "SELECT * FROM cadastro_patrimonio")


def buscar_ativo_por_plaqueta(plaqueta: str) -> pd.DataFrame:
    valor = str(plaqueta).strip()
    if not valor:
        return pd.DataFrame()

    return _read_dataframe(
        PATRIMONIO_DB,
        """
        SELECT *
        FROM cadastro_patrimonio
        WHERE TRIM(REPLACE(CAST(Plaqueta AS TEXT), '.0', '')) = ?
        """,
        (valor,),
    )


def carregar_saidas() -> pd.DataFrame:
    return _read_dataframe(SAIDA_DB, "SELECT * FROM saida ORDER BY Data DESC")


def carregar_retornos() -> pd.DataFrame:
    return _read_dataframe(RETORNO_DB, "SELECT * FROM retorno ORDER BY Data DESC")


def carregar_pendencias_baixa() -> pd.DataFrame:
    return _read_dataframe(
        ESTOQUE_DB,
        "SELECT * FROM pendencias_baixa ORDER BY data_registro DESC",
    )


def carregar_estoque() -> pd.DataFrame:
    return _read_dataframe(ESTOQUE_DB, 'SELECT * FROM estoque')

