"""Clientes somente leitura para as integrações operacionais.

Tokens nunca ficam no código: configure MOVIDESK_TOKEN, ASANA_TOKEN e
ASANA_PROJECT_ID no ambiente ou no arquivo .env local (não versionado).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class ResultadoIntegracao:
    nome: str
    status: str
    mensagem: str
    dados: pd.DataFrame


def _vazio(nome: str, mensagem: str) -> ResultadoIntegracao:
    return ResultadoIntegracao(nome, "NÃO CONFIGURADO", mensagem, pd.DataFrame())


def consultar_movidesk() -> ResultadoIntegracao:
    token = os.getenv("MOVIDESK_TOKEN")
    if not token:
        return _vazio("Movidesk", "Defina MOVIDESK_TOKEN no .env para consultar chamados nesta central.")

    try:
        response = requests.get(
            "https://api.movidesk.com/public/v1/tickets",
            params={
                "token": token,
                "$select": "id,status,baseStatus,subject,createdDate,urgency,lastActionDate,owner",
                "$expand": "owner",
                "$filter": "(ownerTeam eq 'Suporte Técnico')",
                "$orderby": "createdDate desc",
            },
            timeout=15,
        )
        response.raise_for_status()
        linhas = []
        for ticket in response.json():
            owner = ticket.get("owner") or {}
            linhas.append({
                "Chamado": ticket.get("id"),
                "Assunto": ticket.get("subject") or "Sem assunto",
                "Status": ticket.get("status") or ticket.get("baseStatus") or "Não informado",
                "Urgência": ticket.get("urgency") or "Não definida",
                "Criado em": ticket.get("createdDate"),
                "Última ação": ticket.get("lastActionDate"),
                "Responsável": owner.get("businessName") or owner.get("personName") or "Não atribuído",
            })
        return ResultadoIntegracao("Movidesk", "ONLINE", "Chamados atualizados com sucesso.", pd.DataFrame(linhas))
    except requests.RequestException as error:
        return ResultadoIntegracao("Movidesk", "INDISPONÍVEL", f"Não foi possível consultar o Movidesk: {error}", pd.DataFrame())


def consultar_asana() -> ResultadoIntegracao:
    token = os.getenv("ASANA_TOKEN") or os.getenv("TOKEN")
    project_id = os.getenv("ASANA_PROJECT_ID") or os.getenv("PROJECT_ID")
    if not token or not project_id:
        return _vazio("Asana", "Defina ASANA_TOKEN e ASANA_PROJECT_ID no .env para consultar solicitações nesta central.")

    try:
        response = requests.get(
            f"https://app.asana.com/api/1.0/projects/{project_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
            params={"opt_fields": "name,completed,due_on,assignee.name,memberships.section.name,custom_fields.name,custom_fields.display_value"},
            timeout=15,
        )
        response.raise_for_status()
        linhas = []
        for task in response.json().get("data", []):
            campos = {item.get("name"): item.get("display_value") for item in task.get("custom_fields", [])}
            memberships = task.get("memberships") or []
            section = (memberships[0].get("section") or {}).get("name") if memberships else None
            linhas.append({
                "Solicitação": task.get("name") or "Sem título",
                "Concluída": bool(task.get("completed")),
                "Prazo": task.get("due_on") or "Sem prazo",
                "Responsável": (task.get("assignee") or {}).get("name") or "Não atribuído",
                "Etapa": section or "Não informado",
                "Chamado": campos.get("Chamado") or "Não informado",
                "Loja": campos.get("Lojas") or campos.get("Loja") or "Não informado",
            })
        return ResultadoIntegracao("Asana", "ONLINE", "Solicitações atualizadas com sucesso.", pd.DataFrame(linhas))
    except requests.RequestException as error:
        return ResultadoIntegracao("Asana", "INDISPONÍVEL", f"Não foi possível consultar o Asana: {error}", pd.DataFrame())
