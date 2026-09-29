"""Regras de preparação e comparação de relatórios do Senior."""
import pandas as pd
from repositories.senior_repository import carregar_plaquetas_cadastro

COLUNAS_SENIOR = {
    "Unnamed: 0": "Plaqueta", "Unnamed: 1": "Desc. Bem",
    "Unnamed: 8": "Filial", "Unnamed: 9": "Cód. Local",
    "Unnamed: 10": "Desc. Local", "Unnamed: 13": "Cód. Portador",
    "Unnamed: 15": "Portador", "Unnamed: 17": "Data últ. Loc",
    "Unnamed: 19": "Cód. Fornecedor", "Unnamed: 21": "Fornecedor",
    "Unnamed: 25": "Documento", "Unnamed: 27": "Data aquisição",
    "Unnamed: 28": "Valor Aquisição", "Unnamed: 30": "Cód. Bem",
    "Unnamed: 32": "Série Fabricação", "Unnamed: 35": "ESPECIE",
    "Unnamed: 38": "Filial aquisição"
}


def preparar_excel(arquivo):
    df = pd.read_excel(arquivo, usecols=list(COLUNAS_SENIOR.keys()))
    df.rename(columns=COLUNAS_SENIOR, inplace=True)
    df = df[df["Plaqueta"].notna()].copy()
    df["Plaqueta"] = df["Plaqueta"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return df.drop_duplicates(subset=["Plaqueta"], keep="last")


def comparar_com_cadastro(df, db_cadastro="Banco Dados/cadastro_patrimonio.sqlite"):
    atuais = carregar_plaquetas_cadastro(db_cadastro)
    novas = df[~df["Plaqueta"].isin(atuais)]
    existentes = df[df["Plaqueta"].isin(atuais)]
    removidos = sorted(atuais - set(df["Plaqueta"]))
    return novas, existentes, removidos
