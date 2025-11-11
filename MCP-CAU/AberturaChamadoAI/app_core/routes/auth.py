# -*- coding: utf-8 -*-
import uuid
import logging
import json as _json
from flask import Blueprint, request, jsonify, current_app
from ..utils.validators import is_powerfx_expression
from ..services.glpi import buscar_usuario_por_email, autenticar_usuario_por_credenciais


auth_bp = Blueprint("auth", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)


@auth_bp.before_app_request
def ensure_json_headers():
    trace_id = str(uuid.uuid4())[:8]
    logger.info(f"[{trace_id}] {request.method} {request.path}")
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.get_data():
            content_type = request.headers.get('Content-Type', '')
            if not content_type:
                logger.warning(f"[{trace_id}] Content-Type ausente para {request.method}")
            elif not content_type.startswith('application/json'):
                logger.warning(f"[{trace_id}] Content-Type não é JSON: {content_type}")


@auth_bp.route("/authenticate-user", methods=["POST"])
def authenticate_user():
    trace_id = str(uuid.uuid4())[:8]
    try:
        content_type = request.headers.get('Content-Type', '')
        if not content_type or 'application/json' not in content_type.lower():
            return jsonify({
                "sucesso": False,
                "success": False,
                "erro": "bad_request",
                "mensagem": "Content-Type deve ser application/json",
                "detalhe": {"content_type": content_type},
                "trace_id": trace_id,
            }), 400

        # Diagnóstico pré-parse: CT, is_json, preview de bytes e get_json(silent)
        try:
            raw_preview = request.get_data()[:200]
        except Exception:
            raw_preview = b""
        current_app.logger.info("[%s] CT=%s is_json=%s", trace_id, content_type, getattr(request, "is_json", False))
        current_app.logger.info("[%s] DATA_RAW_PREVIEW=%s", trace_id, raw_preview)
        probe = None
        try:
            probe = request.get_json(force=False, silent=True)
        except Exception:
            probe = None
        current_app.logger.info("[%s] GET_JSON(silent)=%s", trace_id, "object" if isinstance(probe, dict) else str(type(probe)))

        # Tentar parsear JSON sem forçar; levantar exceção clara se inválido
        try:
            data = request.get_json(force=False, silent=False)
        except Exception as json_error:
            # Logar apenas os primeiros bytes para depurar sem vazar segredos
            try:
                raw_preview = request.get_data()[:200]
            except Exception:
                raw_preview = b""
            current_app.logger.info("[%s] JSON inválido: %s", trace_id, raw_preview)
            return jsonify({
                "sucesso": False,
                "success": False,
                "erro": "bad_request",
                "mensagem": "JSON inválido",
                "detalhe": {"exception": str(json_error)},
                "trace_id": trace_id,
            }), 400

        if data is None or not isinstance(data, dict):
            # Fallback: tentar remover BOM e parsear manualmente
            try:
                raw_text = request.get_data(as_text=True)
                if raw_text and raw_text[0] == "\ufeff":
                    raw_text = raw_text.lstrip("\ufeff")
                data = _json.loads(raw_text)
            except Exception:
                return jsonify({
                    "sucesso": False,
                    "success": False,
                    "erro": "bad_request",
                    "mensagem": "JSON deve ser um objeto",
                    "trace_id": trace_id,
                }), 400

        # Proteger contra conteúdo não processado pelo Copilot (PowerFx)
        unprocessed = []
        for key, value in data.items():
            if is_powerfx_expression(value):
                unprocessed.append(f"{key}: {value}")
        if unprocessed:
            return jsonify({
                "sucesso": False,
                "success": False,
                "erro": "bad_request",
                "mensagem": "Expressões PowerFx não processadas detectadas",
                "detalhe": {"unprocessed_fields": unprocessed},
                "trace_id": trace_id,
            }), 400

        # Campos de entrada: email OU login, e password. totp_code opcional.
        email = (data.get("email") or data.get("usuario_email") or "").strip()
        login = (data.get("login") or data.get("usuario") or "").strip()
        # Normaliza o login caso o usuário tenha enviado múltiplos campos na mesma mensagem
        if login and ("," in login or " " in login):
            try:
                login = login.split(",")[0].split()[0].strip()
            except Exception:
                login = login.strip()
        password = (data.get("password") or data.get("senha") or "").strip()
        totp_code = (data.get("totp_code") or data.get("totp") or "").strip() or None

        if not password:
            return jsonify({
                "sucesso": False,
                "success": False,
                "erro": "unprocessable_entity",
                "mensagem": "Campo 'password' é obrigatório",
                "trace_id": trace_id,
            }), 422

        resolved_login = login
        resolved_user_id = None
        resolved_email = None
        resolved_name = None

        if not resolved_login:
            if not email or "@" not in email:
                return jsonify({
                    "sucesso": False,
                    "success": False,
                    "erro": "unprocessable_entity",
                    "mensagem": "Informe 'login' ou 'email' válido",
                    "trace_id": trace_id,
                }), 422
            lookup = buscar_usuario_por_email(email)
            if not lookup.get("found"):
                return jsonify({
                    "sucesso": False,
                    "success": False,
                    "erro": "not_found",
                    "mensagem": "Usuário não encontrado no GLPI pelo e-mail",
                    "query_email": email,
                    "trace_id": trace_id,
                }), 404
            resolved_login = lookup.get("login") or ""
            resolved_user_id = lookup.get("user_id")
            resolved_email = lookup.get("email")
            resolved_name = lookup.get("name")

        # Autenticar com login/password no GLPI (REST)
        auth_result = autenticar_usuario_por_credenciais(resolved_login, password, totp_code)

        # Mapear falhas de autenticação para 401/fluxo previsível no Copilot
        status = str(auth_result.get("status") or "").lower()
        if status and status != "ok":
            if status == "unauthorized":
                return jsonify({
                    "sucesso": False,
                    "success": False,
                    "erro": "unauthorized",
                    "mensagem": "Login ou senha inválidos",
                    "detalhe": {"reason": auth_result.get("reason")},
                    "trace_id": trace_id,
                }), 401
            if status == "totp_required":
                return jsonify({
                    "sucesso": False,
                    "success": False,
                    "erro": "mfa_required",
                    "mensagem": "Autenticação requer TOTP (code)",
                    "detalhe": {"reason": auth_result.get("reason")},
                    "trace_id": trace_id,
                }), 401

        # Montar resposta sem expor a senha
        response_data = {
            "sucesso": True,
            "success": True,
            "trace_id": trace_id,
            "usuario": {
                "login": resolved_login,
                "user_id": auth_result.get("user_id") or resolved_user_id,
                "email": resolved_email,
                "name": resolved_name,
            },
            "auth": {
                "status": auth_result.get("status"),
                "logout_verified": auth_result.get("logout_verified", False),
            },
        }
        return jsonify(response_data), 200
    except Exception as e:
        # Não logar senha; retornar erro genérico
        return jsonify({
            "sucesso": False,
            "success": False,
            "erro": "internal_error",
            "mensagem": str(e),
            "trace_id": trace_id,
        }), 500