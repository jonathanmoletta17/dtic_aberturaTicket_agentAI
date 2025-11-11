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


def autenticar_usuario_por_credenciais(login: str, password: str, totp_code: str | None = None) -> Dict[str, Any]:
    """
    Inicia uma sessão no GLPI usando login/senha do usuário, obtém o glpiID ativo,
    coleta metadados mínimos (nome/email) e encerra a sessão, retornando status.

    Observações:
    - Não loga nem retorna senha.
    - Suporta TOTP (se configurado no GLPI) via campo "code".
    - Valida pós-logout que o token foi invalidado.
    """
    if not login or not password:
        raise ValueError("Login e password são obrigatórios")

    settings = load_settings()
    headers = {
        "App-Token": settings.glpi_app_token or "",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {"login": login, "password": password}
    if totp_code:
        # Campo comum para TOTP nas versões recentes é 'code'
        payload["code"] = totp_code

    # 1) initSession
    resp = requests.post(f"{settings.glpi_url}/initSession", json=payload, headers=headers, timeout=15)
    # Tratar explicitamente falhas de autenticação como estado estruturado
    if resp.status_code == 401:
        reason = None
        try:
            j = resp.json()
            reason = j.get("message") or j.get("error")
        except Exception:
            reason = None
        # Se houver indicação de TOTP/code, sinalizar claramente
        if not totp_code and reason and ("code" in str(reason).lower() or "totp" in str(reason).lower()):
            return {
                "status": "totp_required",
                "login": login,
                "reason": str(reason),
            }
        return {
            "status": "unauthorized",
            "login": login,
            "reason": str(reason) if reason else resp.text,
        }
    resp.raise_for_status()
    data = resp.json()
    session_token = data.get("session_token")
    if not session_token:
        raise RuntimeError("Session token não retornado pelo GLPI")

    session_headers = {**headers, "Session-Token": session_token}

    # 2) getFullSession -> glpiID
    uid: Any = None
    try:
        s = requests.get(f"{settings.glpi_url}/getFullSession", headers=session_headers, timeout=10)
        if s.ok:
            sdata = s.json()
            uid = sdata.get("glpiID")
    except Exception:
        pass

    # 3) Buscar metadados pelo login (melhorar resposta para Copilot) via helper centralizado
    user_name = None
    user_email = None
    try:
        res_busca = buscar_usuario_glpi(login=login, headers=session_headers)
        if res_busca.get("found") and isinstance(res_busca.get("user"), dict):
            info = res_busca["user"]
            user_name = info.get("name")
            user_email = info.get("email")
            if uid is None and isinstance(info.get("id"), int):
                uid = info.get("id")
    except Exception:
        # Metadados são auxiliares; não interromper o fluxo
        pass

    # 4) Encerrar sessão
    logout_verified = False
    try:
        k = requests.post(f"{settings.glpi_url}/killSession", headers=session_headers, timeout=10)
        k.raise_for_status()
        # Verificar se token foi invalidado
        chk = requests.get(f"{settings.glpi_url}/getFullSession", headers=session_headers, timeout=8)
        logout_verified = (chk.status_code == 401) or (not chk.ok)
    except Exception:
        logout_verified = False

    return {
        "status": "ok",
        "user_id": uid if isinstance(uid, int) else None,
        "login": login,
        "name": user_name,
        "email": user_email,
        "logout_verified": logout_verified,
    }


def buscar_usuario_por_email(email: str) -> Dict[str, Any]:
    if not email or not isinstance(email, str):
        raise ValueError("E-mail inválido para busca no GLPI")

    try:
        headers = autenticar_glpi()
        email_normalizado = email.strip()
        res = buscar_usuario_glpi(email=email_normalizado, headers=headers)
        user_info = res.get("user") if isinstance(res.get("user"), dict) else None
        found = bool(user_info and user_info.get("id"))
        return {
            "found": found,
            "user_id": user_info.get("id") if user_info else None,
            "name": user_info.get("name") if user_info else None,
            "login": user_info.get("login") if user_info else None,
            "email": user_info.get("email") if user_info else email_normalizado,
            "raw": res.get("raw"),
        }
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por e-mail no GLPI: {str(e)}")
        raise


def criar_ticket_glpi(dados: Dict[str, Any]) -> int:
    logger.info("=== INICIANDO CRIAÇÃO DE TICKET NO GLPI ===")
    settings = load_settings()
    headers = autenticar_glpi()

    impact_raw = (dados.get("impact", "MEDIO") or "MEDIO").upper()
    # Se urgência não for fornecida, usar o mesmo nível do impacto
    urgency_input = dados.get("urgency")
    urgency_raw = (urgency_input or impact_raw or "MEDIA").upper()
    # Defaults alinhados com GLPI (Média)
    impact = IMPACT_MAP.get(impact_raw, 3)
    urgency = URGENCY_MAP.get(urgency_raw, 3)
    # Prioridade como o maior entre impacto e urgência
    priority = max(impact, urgency)

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

def buscar_usuario_glpi(login: str | None = None, email: str | None = None, headers: Dict[str, str] | None = None) -> Dict[str, Any]:
    """
    Busca usuário no GLPI por login ou e-mail usando o endpoint /search/User.

    - Tenta match exato (equals) e, se necessário, match parcial (contains).
    - Retorna estrutura padronizada com id, name, login, email e o JSON bruto.
    - Pode reutilizar um cabeçalho de sessão já autenticado (headers) ou autenticará automaticamente.
    """
    if not login and not email:
        raise ValueError("Informe ao menos 'login' ou 'email' para busca no GLPI")

    settings = load_settings()
    if headers is None:
        headers = autenticar_glpi()

    url_search = f"{settings.glpi_url}/search/User"

    def _extract_rows(data_obj: Any) -> list:
        if isinstance(data_obj, dict):
            if isinstance(data_obj.get("data"), list):
                return data_obj.get("data")
            if isinstance(data_obj.get("rows"), list):
                return data_obj.get("rows")
        return []

    # Define campo e valor de busca
    if email:
        campo = 5  # email
        valor = email.strip()
    else:
        campo = 1  # login
        valor = str(login).strip()

    base_forcedisplay = {
        "forcedisplay[0]": 1,
        "forcedisplay[1]": 2,
        "forcedisplay[2]": 5,
        "forcedisplay[3]": 9,
    }

    params_equals = {
        **base_forcedisplay,
        "criteria[0][field]": campo,
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": valor,
    }
    params_contains = {
        **base_forcedisplay,
        "criteria[0][field]": campo,
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": valor,
    }

    try:
        resp = requests.get(url_search, headers=headers, params=params_equals, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rows = _extract_rows(data)

        # Se não encontrou nada, tenta contains
        if not rows:
            resp2 = requests.get(url_search, headers=headers, params=params_contains, timeout=10)
            resp2.raise_for_status()
            data2 = resp2.json()
            rows = _extract_rows(data2)
            if rows:
                data = data2

        selected = None
        user_info = None
        if rows:
            # Preferir match exato por campo
            if isinstance(rows[0], dict):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    # chave 1 (login) ou 5 (email) conforme critério de busca
                    chave = str(row.get(str(campo), "")).strip().lower()
                    if chave == valor.strip().lower():
                        selected = row
                        break
                if not selected:
                    selected = rows[0]
                item = selected
                # Extrai campos padronizados
                uid = item.get("id") or item.get("users_id") or item.get("2")
                uname = item.get("name") or item.get("realname") or item.get("1") or item.get("9")
                ulogin = item.get("login") or item.get("user_name") or item.get("9") or item.get("1")
                uemail = item.get("email") or item.get("user_email") or item.get("5")
                try:
                    if isinstance(uid, str) and uid.isdigit():
                        uid = int(uid)
                except Exception:
                    pass
                user_info = {"id": uid, "name": uname, "login": ulogin, "email": uemail}
            elif isinstance(rows[0], list):
                item = rows[0]
                user_info = {
                    "id": item[0] if len(item) > 0 else None,
                    "name": item[1] if len(item) > 1 else None,
                    "email": item[2] if len(item) > 2 else None,
                    "login": item[3] if len(item) > 3 else None,
                }

        found = bool(user_info and user_info.get("id"))
        return {"found": found, "user": user_info, "raw": data}
    except Exception as e:
        logger.error(f"Erro ao buscar usuário no GLPI: {str(e)}")
        raise


