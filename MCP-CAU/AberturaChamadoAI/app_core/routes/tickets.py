# -*- coding: utf-8 -*-
import uuid
import logging
from flask import Blueprint, request, jsonify
from ..services.glpi import criar_ticket_glpi, buscar_usuario_por_email, mapear_categoria
from ..config import load_settings
from ..utils.validators import is_powerfx_expression


tickets_bp = Blueprint("tickets", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)


@tickets_bp.before_app_request
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


@tickets_bp.route("/glpi-user-by-email", methods=["GET"])
def glpi_user_by_email():
    try:
        email = request.args.get("email") or request.args.get("e") or request.args.get("mail")
        if not email or "@" not in email:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Parâmetro 'email' é obrigatório",
                "erro": "Parâmetro 'email' é obrigatório",
            }), 400
        result = buscar_usuario_por_email(email)
        return jsonify({
            "sucesso": True,
            "success": True,
            "query_email": email,
            "resultado": result,
        }), 200
    except Exception as e:
        return jsonify({"sucesso": False, "success": False, "error": str(e), "erro": str(e)}), 500


@tickets_bp.route("/create-ticket-complete", methods=["POST"])
def create_ticket_complete():
    trace_id = str(uuid.uuid4())[:8]
    try:
        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Content-Type deve ser 'application/json'",
                "erro": "Content-Type deve ser 'application/json'",
                "details": {
                    "received_content_type": content_type,
                    "expected_content_type": "application/json",
                },
                "trace_id": trace_id,
            }), 400

        raw_data = request.get_data()
        if not raw_data:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Corpo da requisição vazio",
                "erro": "Corpo da requisição vazio",
                "trace_id": trace_id,
            }), 400

        try:
            data = request.get_json(force=True, silent=False)
        except Exception as json_error:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": f"JSON malformado: {str(json_error)}",
                "erro": f"JSON malformado: {str(json_error)}",
                "trace_id": trace_id,
            }), 400

        if data is None or not isinstance(data, dict):
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "JSON deve ser um objeto",
                "erro": "JSON deve ser um objeto",
                "trace_id": trace_id,
            }), 400

        powerfx_fields = []
        for key, value in data.items():
            if is_powerfx_expression(value):
                powerfx_fields.append(f"{key}: {value}")
        if powerfx_fields:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Expressões PowerFx não processadas detectadas",
                "erro": "O Copilot Studio não processou as expressões PowerFx corretamente. Verifique a configuração do agente.",
                "details": {
                    "unprocessed_fields": powerfx_fields,
                },
                "trace_id": trace_id,
            }), 400

        description = data.get('description') or data.get('descricao')
        title = data.get('title') or data.get('titulo')
        category = data.get('category') or data.get('categoria')
        impact = data.get('impact') or data.get('impacto')
        location = data.get('location') or data.get('localizacao')
        contact_phone = data.get('contact_phone') or data.get('telefone_contato') or data.get('telefone')
        requester_email = data.get('requester_email') or data.get('email') or data.get('usuario_email')

        glpi_category = mapear_categoria(category)

        if not description:
            return jsonify({"sucesso": False, "success": False, "error": "Campo 'description/descricao' é obrigatório", "erro": "Campo 'description/descricao' é obrigatório", "trace_id": trace_id}), 400

        content_parts_validate = [description or ""]
        if location:
            content_parts_validate.append(f"Local: {location}")
        if contact_phone:
            content_parts_validate.append(f"Telefone: {contact_phone}")
        if category:
            content_parts_validate.append(f"Categoria: {category}")
        full_content_validate = "\n\n".join(filter(None, content_parts_validate))
        if len(full_content_validate.strip()) < 50:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Descrição muito curta",
                "erro": "O conteúdo total do chamado está curto. Inclua mais detalhes.",
                "details": {"current_length": len(full_content_validate.strip()), "required_length": 50},
                "trace_id": trace_id,
            }), 400

        vague_words = ['problema', 'erro', 'não funciona', 'quebrado', 'ruim', 'lento', 'travando', 'bug']
        description_lower = description.lower()
        found_vague_words = [word for word in vague_words if word in description_lower]
        if found_vague_words and len(full_content_validate.strip()) < 100:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Descrição muito vaga",
                "erro": "Por favor, seja mais específico.",
                "trace_id": trace_id,
            }), 400

        if not contact_phone or len(contact_phone.strip()) < 8:
            return jsonify({"sucesso": False, "success": False, "error": "Telefone inválido", "erro": "Telefone inválido", "trace_id": trace_id}), 400
        if not title:
            return jsonify({"sucesso": False, "success": False, "error": "Campo 'title/titulo' é obrigatório", "erro": "Campo 'title/titulo' é obrigatório", "trace_id": trace_id}), 400
        if not category:
            return jsonify({"sucesso": False, "success": False, "error": "Campo 'category/categoria' é obrigatório", "erro": "Campo 'category/categoria' é obrigatório", "trace_id": trace_id}), 400
        if not impact:
            return jsonify({"sucesso": False, "success": False, "error": "Campo 'impact/impacto' é obrigatório", "erro": "Campo 'impact/impacto' é obrigatório", "trace_id": trace_id}), 400
        if not location or len(location.strip()) < 3:
            return jsonify({"sucesso": False, "success": False, "error": "Localização inválida", "erro": "Localização inválida", "trace_id": trace_id}), 400

        settings = load_settings()
        if not all([settings.glpi_url, settings.glpi_app_token, settings.glpi_user_token]):
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Configurações do GLPI não encontradas. Verifique o arquivo .env",
                "erro": "Configurações do GLPI não encontradas. Verifique o arquivo .env",
                "trace_id": trace_id,
            }), 500

        normalized_data = {
            'description': description,
            'title': title,
            'category': glpi_category,
            'category_user_friendly': category,
            'impact': impact,
            'location': location,
            'contact_phone': contact_phone,
            'requester_email': requester_email,
        }

        requester_lookup = None
        if requester_email:
            try:
                requester_lookup = buscar_usuario_por_email(requester_email)
                if requester_lookup.get("found") and requester_lookup.get("user_id"):
                    normalized_data["users_id_recipient"] = requester_lookup["user_id"]
                    normalized_data["users_id_requester"] = requester_lookup["user_id"]
            except Exception:
                pass

        ticket_id = criar_ticket_glpi(normalized_data)

        response_data = {
            "sucesso": True,
            "success": True,
            "message": f"Chamado #{ticket_id} criado com sucesso!",
            "ticket_id": ticket_id,
            "trace_id": trace_id,
            "categoria": category,
            "details": {
                "title": title,
                "category": category,
                "impact": impact,
                "location": location,
                "requester_email": requester_email,
                "requester": {
                    "found": bool(requester_lookup and requester_lookup.get("found")),
                    "user_id": requester_lookup.get("user_id") if requester_lookup else None,
                    "name": requester_lookup.get("name") if requester_lookup else None,
                    "login": requester_lookup.get("login") if requester_lookup else None,
                } if requester_email else None,
            },
        }
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({"sucesso": False, "success": False, "error": str(e), "erro": str(e), "trace_id": trace_id}), 500


