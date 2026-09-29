"""Regras e consultas do Assistente de TI.

Esta camada concentra somente a leitura e a interpretação simples das
perguntas. A interface Streamlit permanece em modulos/assistente_ti.py.
"""

from __future__ import annotations

import pandas as pd

from repositories import assistente_repository


def _normalizar_plaqueta(valor: object) -> str:
    """Normaliza plaquetas para permitir comparações entre bancos."""
    if valor is None or pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto


def carregar_resumo_operacional() -> dict[str, int]:
    """Monta os indicadores exibidos no Assistente de TI."""
    ativos = assistente_repository.carregar_ativos()
    saidas = assistente_repository.carregar_saidas()
    retornos = assistente_repository.carregar_retornos()
    baixas = assistente_repository.carregar_pendencias_baixa()
    estoque = assistente_repository.carregar_estoque()

    plaquetas_retornadas = {
        _normalizar_plaqueta(valor)
        for valor in retornos.get("Patrimonio", pd.Series(dtype=str))
    }
    plaquetas_saidas = {
        _normalizar_plaqueta(valor)
        for valor in saidas.get("Patrimonio", pd.Series(dtype=str))
    }
    pendentes = len({valor for valor in plaquetas_saidas if valor and valor not in plaquetas_retornadas})

    itens_estoque = 0
    if not estoque.empty and "Qtde Estoque" in estoque.columns:
        itens_estoque = int(pd.to_numeric(estoque["Qtde Estoque"], errors="coerce").fillna(0).sum())

    pendencias_abertas = len(baixas)
    if not baixas.empty and "status" in baixas.columns:
        status = baixas["status"].astype(str).str.lower().str.strip()
        pendencias_abertas = int((~status.isin({"concluído", "concluido", "finalizado", "baixado"})).sum())

    return {
        "ativos": int(len(ativos)),
        "saidas_sem_retorno": pendentes,
        "pendencias_baixa": pendencias_abertas,
        "itens_estoque": itens_estoque,
    }


def listar_saidas_sem_retorno() -> pd.DataFrame:
    """Retorna patrimônios que possuem saída e nenhum retorno registrado."""
    saidas = assistente_repository.carregar_saidas()
    retornos = assistente_repository.carregar_retornos()
    if saidas.empty:
        return pd.DataFrame()

    retornadas = {
        _normalizar_plaqueta(valor)
        for valor in retornos.get("Patrimonio", pd.Series(dtype=str))
    }
    resultado = saidas.copy()
    resultado["_plaqueta_normalizada"] = resultado["Patrimonio"].map(_normalizar_plaqueta)
    resultado = resultado[resultado["_plaqueta_normalizada"].ne("")]
    resultado = resultado[~resultado["_plaqueta_normalizada"].isin(retornadas)]
    return resultado.drop(columns=["_plaqueta_normalizada"], errors="ignore")


def listar_pendencias_baixa() -> pd.DataFrame:
    """Retorna as pendências de baixa ainda não concluídas."""
    dados = assistente_repository.carregar_pendencias_baixa()
    if dados.empty or "status" not in dados.columns:
        return dados
    status = dados["status"].astype(str).str.lower().str.strip()
    return dados[~status.isin({"concluído", "concluido", "finalizado", "baixado"})].copy()


def buscar_ativo(plaqueta: str) -> pd.DataFrame:
    """Busca um patrimônio pelo número informado pelo usuário."""
    return assistente_repository.buscar_ativo_por_plaqueta(_normalizar_plaqueta(plaqueta))


def interpretar_pergunta(pergunta: str) -> tuple[str, pd.DataFrame | None]:
    """Responde perguntas operacionais simples sem depender de IA externa."""
    texto = str(pergunta).strip().lower()
    if not texto:
        return "Digite uma pergunta para consultar o sistema.", None

    if "quantos" in texto and ("ativo" in texto or "patrimônio" in texto or "patrimonio" in texto):
        resumo = carregar_resumo_operacional()
        return f"O cadastro possui {resumo['ativos']:,} ativos.".replace(",", "."), None

    if "saída" in texto or "saida" in texto:
        dados = listar_saidas_sem_retorno()
        return f"Encontrei {len(dados)} saída(s) sem retorno registrado.", dados

    if "baixa" in texto and ("pend" in texto or "aberta" in texto):
        dados = listar_pendencias_baixa()
        return f"Existem {len(dados)} pendência(s) de baixa em aberto.", dados

    palavras = texto.replace("?", " ").split()
    for palavra in palavras:
        numero = "".join(ch for ch in palavra if ch.isdigit())
        if numero and len(numero) >= 3:
            dados = buscar_ativo(numero)
            if not dados.empty:
                return f"Localizei a plaqueta {numero} no cadastro de patrimônio.", dados

    return (
        "Ainda não reconheço essa pergunta. Tente algo como: "
        "'quantos ativos temos?', 'quais saídas estão sem retorno?' "
        "ou informe uma plaqueta, por exemplo 81940."
    ), None
