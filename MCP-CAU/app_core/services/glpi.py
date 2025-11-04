# -*- coding: utf-8 -*-
import logging
import json as _json
from typing import Any, Dict
import requests
from ..config import load_settings
from ..domain.mappings import IMPACT_MAP, URGENCY_MAP, CATEGORY_MAP


logger = logging.getLogger(__name__)


def mapear_categoria(category_user_friendly):
    if not category_user_friendly:
        return CATEGORY_MAP["OUTROS"]["glpi_category_id"]
    if isinstance(category_user_friendly, int):
        return category_user_friendly
    category_key = str(category_user_friendly).strip().upper()
    if category_key in CATEGORY_MAP:
        return CATEGORY_MAP[category_key]["glpi_category_id"]
    logger.warning(f"Categoria não encontrada: {category_user_friendly}. Usando categoria padrão.")
    return CATEGORY_MAP["OUTROS"]["glpi_category_id"]


def autenticar_glpi() -> Dict[str, str]:
    settings = load_settings()
    headers = {
        "App-Token": settings.glpi_app_token or "",
        "Authorization": f"user_token {settings.glpi_user_token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            f"{settings.glpi_url}/initSession",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        session_token = data.get("session_token")
        if not session_token:
            raise RuntimeError("Session token não encontrado na resposta do GLPI")
        return {
            "App-Token": settings.glpi_app_token or "",
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }
    except Exception as e:
        logger.error(f"Erro na autenticação GLPI: {str(e)}")
        raise


def buscar_usuario_por_email(email: str) -> Dict[str, Any]:
    if not email or not isinstance(email, str):
        raise ValueError("E-mail inválido para busca no GLPI")

    headers = autenticar_glpi()
    email_normalizado = email.strip()
    settings = load_settings()
    url_search = f"{settings.glpi_url}/search/User"

    params_equals = {
        "criteria[0][field]": 5,
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": email_normalizado,
        "forcedisplay[0]": 1,
        "forcedisplay[1]": 2,
        "forcedisplay[2]": 5,
        "forcedisplay[3]": 9,
    }
    params_contains = {
        "criteria[0][field]": 5,
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": email_normalizado,
        "forcedisplay[0]": 1,
        "forcedisplay[1]": 2,
        "forcedisplay[2]": 5,
        "forcedisplay[3]": 9,
    }

    try:
        resp = requests.get(url_search, headers=headers, params=params_equals, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rows = []
        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                rows = data.get("data")
            elif isinstance(data.get("rows"), list):
                rows = data.get("rows")

        if not rows:
            resp2 = requests.get(url_search, headers=headers, params=params_contains, timeout=10)
            resp2.raise_for_status()
            data2 = resp2.json()
            if isinstance(data2, dict):
                if isinstance(data2.get("data"), list):
                    rows = data2.get("data")
                elif isinstance(data2.get("rows"), list):
                    rows = data2.get("rows")
            if rows:
                data = data2

        user_info = None
        if rows:
            item = rows[0]
            if isinstance(item, dict):
                uid = item.get("id") or item.get("users_id")
                uname = item.get("name") or item.get("realname")
                ulogin = item.get("login") or item.get("user_name")
                uemail = item.get("email") or item.get("user_email")
                if uid is None and any(k in item for k in ["1", "2", "5", "9"]):
                    try:
                        uid = item.get("2") or uid
                    except Exception:
                        uid = uid
                    uname = uname or item.get("1") or item.get("9")
                    uemail = uemail or item.get("5")
                    ulogin = ulogin or item.get("9") or item.get("1")
                user_info = {"id": uid, "name": uname, "login": ulogin, "email": uemail}
            elif isinstance(item, list):
                user_info = {
                    "id": item[0] if len(item) > 0 else None,
                    "name": item[1] if len(item) > 1 else None,
                    "email": item[2] if len(item) > 2 else None,
                    "login": item[3] if len(item) > 3 else None,
                }

        found = bool(user_info and user_info.get("id"))
        return {
            "found": found,
            "user_id": user_info.get("id") if user_info else None,
            "name": user_info.get("name") if user_info else None,
            "login": user_info.get("login") if user_info else None,
            "email": user_info.get("email") if user_info else email_normalizado,
            "raw": data,
        }
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por e-mail no GLPI: {str(e)}")
        raise


def criar_ticket_glpi(dados: Dict[str, Any]) -> int:
    logger.info("=== INICIANDO CRIAÇÃO DE TICKET NO GLPI ===")
    settings = load_settings()
    headers = autenticar_glpi()

    impact_raw = (dados.get("impact", "MEDIO") or "MEDIO").upper()
    urgency_raw = (dados.get("urgency", "MEDIA") or "MEDIA").upper()
    impact = IMPACT_MAP.get(impact_raw, 2)
    urgency = URGENCY_MAP.get(urgency_raw, 2)
    priority = min(5, max(1, (impact + urgency) // 2))

    category_raw = dados.get("category")
    category_id = mapear_categoria(category_raw)

    content_parts = [dados.get("description", "")]
    if dados.get("location"):
        content_parts.append(f"Local: {dados['location']}")
    if dados.get("contact_phone"):
        content_parts.append(f"Telefone: {dados['contact_phone']}")
    if dados.get("category"):
        content_parts.append(f"Categoria: {dados['category']}")
    content = "\n\n".join(filter(None, content_parts))

    payload = {
        "input": {
            "name": dados.get("title", "Chamado via Copilot Studio"),
            "content": content,
            "itilcategories_id": category_id,
            "type": 1,
            "urgency": urgency,
            "impact": impact,
            "priority": priority,
            "status": 2,
            "entities_id": 1,
        }
    }

    requester_user_id = dados.get("users_id_recipient")
    if requester_user_id:
        payload["input"]["users_id_recipient"] = requester_user_id
    requester_actor_id = dados.get("users_id_requester") or dados.get("users_id_recipient")
    if requester_actor_id:
        payload["input"]["_users_id_requester"] = requester_actor_id

    payload_json = _json.dumps(payload, ensure_ascii=False)
    headers_with_charset = headers.copy()
    headers_with_charset["Content-Type"] = "application/json; charset=utf-8"

    response = requests.post(
        f"{settings.glpi_url}/Ticket",
        headers=headers_with_charset,
        data=payload_json.encode('utf-8'),
        timeout=10,
    )

    if response.status_code != 201:
        raise RuntimeError(f"GLPI retornou status {response.status_code}: {response.text}")

    result = response.json()
    ticket_id = result.get("id")
    if not ticket_id:
        raise RuntimeError("ID do ticket não retornado pelo GLPI")
    return ticket_id


