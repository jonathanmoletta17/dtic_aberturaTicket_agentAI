# app.py - Agente Copilot Studio para Criação de Tickets GLPI
# -*- coding: utf-8 -*-
"""
Sistema de Abertura de Chamados GLPI via Copilot Studio
======================================================

Este sistema integra o Microsoft Copilot Studio com o GLPI para criação
automatizada de tickets de suporte técnico.

Funcionalidades:
- Criação de tickets via API REST
- Validação de dados de entrada
- Mapeamento de categorias user-friendly
- Tratamento de erros e logging
- Validação de expressões PowerFx não processadas

Autor: Sistema MCP-CAU
Versão: 2.0
"""

import os
import uuid
import json
import logging
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa aplicação Flask
app = Flask(__name__)

# Configuração de encoding UTF-8 e formatação JSON
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ========== MIDDLEWARE PARA HEADERS PADRONIZADOS ==========
@app.before_request
def ensure_json_headers():
    """
    Middleware que garante headers padronizados para requisições JSON.
    
    Funcionalidades:
    - Adiciona Content-Type se ausente em métodos POST/PUT/PATCH
    - Adiciona Accept se ausente
    - Registra informações detalhadas da requisição
    """
    trace_id = str(uuid.uuid4())[:8]
    
    # Log detalhado da requisição
    logger.info(f"[{trace_id}] {request.method} {request.path}")
    logger.info(f"[{trace_id}] Headers: {dict(request.headers)}")
    logger.info(f"[{trace_id}] Content-Type: {request.headers.get('Content-Type', 'ausente')}")
    logger.info(f"[{trace_id}] User-Agent: {request.headers.get('User-Agent', 'ausente')}")
    
    # Para métodos que enviam dados, garantir headers corretos
    if request.method in ['POST', 'PUT', 'PATCH']:
        # Verificar se há dados no corpo
        if request.get_data():
            content_type = request.headers.get('Content-Type', '')
            
            # Se não há Content-Type ou está incorreto, sugerir correção
            if not content_type:
                logger.warning(f"[{trace_id}] Content-Type ausente para {request.method}")
            elif not content_type.startswith('application/json'):
                logger.warning(f"[{trace_id}] Content-Type não é JSON: {content_type}")

# Configurações do GLPI obtidas do ambiente
GLPI_URL = os.getenv("GLPI_URL")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

# Mapeamentos para o GLPI
IMPACT_MAP = {
    "BAIXO": 1,
    "MEDIO": 2, 
    "ALTO": 3,
    "MUITO_ALTO": 4,
    "CRITICO": 5
}

URGENCY_MAP = {
    "BAIXA": 1,
    "MEDIA": 2,
    "ALTA": 3,
    "MUITO_ALTA": 4,
    "CRITICA": 5
}

# Mapeamento de categorias user-friendly para categorias GLPI
CATEGORY_MAP = {
    "HARDWARE_COMPUTADOR": {
        "display": "🖥️ HARDWARE - Computador/Notebook",
        "glpi_category": "Tipos de computador",
        "glpi_subcategory": "Desktop",
        "glpi_category_id": 1  # ID da categoria no GLPI
    },
    "HARDWARE_IMPRESSORA": {
        "display": "🖨️ HARDWARE - Impressora",
        "glpi_category": "Tipos de impressora", 
        "glpi_subcategory": "Impressora laser",
        "glpi_category_id": 2  # ID da categoria no GLPI
    },
    "HARDWARE_MONITOR": {
        "display": "📺 HARDWARE - Monitor/Equipamentos",
        "glpi_category": "Tipos de monitor",
        "glpi_subcategory": "Monitor LCD",
        "glpi_category_id": 3  # ID da categoria no GLPI
    },
    "SOFTWARE": {
        "display": "💻 SOFTWARE - Aplicativos/Programas",
        "glpi_category": "Categorias de software",
        "glpi_subcategory": "Software de escritório",
        "glpi_category_id": 4  # ID da categoria no GLPI
    },
    "CONECTIVIDADE": {
        "display": "🌐 CONECTIVIDADE - Internet/Rede",
        "glpi_category": "Redes",
        "glpi_subcategory": "Redes WiFi",
        "glpi_category_id": 5  # ID da categoria no GLPI
    },
    "SEGURANCA": {
        "display": "🔐 SEGURANÇA - Acesso/Login",
        "glpi_category": "Categorias ITIL",
        "glpi_subcategory": "Gestão de identidade",
        "glpi_category_id": 6  # ID da categoria no GLPI
    },
    "SOLICITACAO": {
        "display": "📋 SOLICITAÇÃO - Instalação/Configuração",
        "glpi_category": "Assistência",
        "glpi_subcategory": "Instalação de software",
        "glpi_category_id": 7  # ID da categoria no GLPI
    },
    "OUTROS": {
        "display": "❓ OUTROS - Não listado acima",
        "glpi_category": "Geral",
        "glpi_subcategory": "Problemas diversos",
        "glpi_category_id": 8  # ID da categoria no GLPI
    }
}

def mapear_categoria(category_user_friendly):
    """Mapeia categoria user-friendly para ID de categoria GLPI"""
    if not category_user_friendly:
        # Usa categoria OUTROS como padrão para entradas vazias
        return CATEGORY_MAP["OUTROS"]["glpi_category_id"]
    
    # Se já for um inteiro (ID), retorna ele mesmo
    if isinstance(category_user_friendly, int):
        return category_user_friendly
    
    # Normaliza entrada (remove espaços e converte para maiúsculo)
    category_key = str(category_user_friendly).strip().upper()
    
    # Busca no mapeamento
    if category_key in CATEGORY_MAP:
        return CATEGORY_MAP[category_key]["glpi_category_id"]
    
    # Se não encontrar, retorna ID da categoria padrão
    logger.warning(f"Categoria não encontrada: {category_user_friendly}. Usando categoria padrão.")
    # Usa categoria OUTROS como fallback quando não há correspondência
    return CATEGORY_MAP["OUTROS"]["glpi_category_id"]

def autenticar_glpi():
    """Autentica no GLPI e retorna headers com session token"""
    headers = {
        "App-Token": GLPI_APP_TOKEN,
        "Authorization": f"user_token {GLPI_USER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(
            f"{GLPI_URL}/initSession", 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        session_token = data.get("session_token")
        
        if not session_token:
            raise RuntimeError("Session token não encontrado na resposta do GLPI")
            
        return {
            "App-Token": GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }
        
    except Exception as e:
        logger.error(f"Erro na autenticação GLPI: {str(e)}")
        raise

def buscar_usuario_por_email(email):
    """Busca usuário do GLPI pelo e-mail e retorna dados essenciais.

    Retorna dict com chaves: found (bool), user_id (int|None), name, login, email, raw.
    """
    if not email or not isinstance(email, str):
        raise ValueError("E-mail inválido para busca no GLPI")

    headers = autenticar_glpi()
    email_normalizado = email.strip()

    # Endpoint de busca genérica por usuários no GLPI
    url_search = f"{GLPI_URL}/search/User"

    # Critério padrão: igualdade exata por e-mail
    params_equals = {
        "criteria[0][field]": 5,            # Campo 'email' (instalações GLPI comuns)
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": email_normalizado,
        "forcedisplay[0]": 1,               # id
        "forcedisplay[1]": 2,               # name
        "forcedisplay[2]": 5,               # email
        "forcedisplay[3]": 9                # login
    }
    # Fallback: contém e-mail (caso igualdade não retorne)
    params_contains = {
        "criteria[0][field]": 5,
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": email_normalizado,
        "forcedisplay[0]": 1,
        "forcedisplay[1]": 2,
        "forcedisplay[2]": 5,
        "forcedisplay[3]": 9
    }

    try:
        # 1) Tenta igualdade exata
        resp = requests.get(url_search, headers=headers, params=params_equals, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Estruturas possíveis: 'data' (GLPI 10) ou 'rows' (variações)
        rows = []
        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                rows = data.get("data")
            elif isinstance(data.get("rows"), list):
                rows = data.get("rows")

        # 2) Se não achou nada, tenta busca por "contains"
        if not rows:
            resp2 = requests.get(url_search, headers=headers, params=params_contains, timeout=10)
            resp2.raise_for_status()
            data2 = resp2.json()
            if isinstance(data2, dict):
                if isinstance(data2.get("data"), list):
                    rows = data2.get("data")
                elif isinstance(data2.get("rows"), list):
                    rows = data2.get("rows")
            # Mantém o último raw para depuração
            if rows:
                data = data2

        user_info = None
        if rows:
            # Pega a primeira correspondência
            item = rows[0]
            # Algumas instalações retornam dict com chaves semânticas;
            # outras retornam chaves numéricas ("1","2","5","9") conforme forcedisplay.
            if isinstance(item, dict):
                # Tenta primeiro pelas chaves semânticas
                uid = item.get("id") or item.get("users_id")
                uname = item.get("name") or item.get("realname")
                ulogin = item.get("login") or item.get("user_name")
                uemail = item.get("email") or item.get("user_email")

                # Se veio no formato numérico, usa mapeamento dos forcedisplay
                if uid is None and any(k in item for k in ["1","2","5","9"]):
                    # Pelo raw observado: "2" parece ser id, "1" nome, "5" email, "9" login
                    try:
                        uid = item.get("2") or uid
                    except Exception:
                        uid = uid
                    uname = uname or item.get("1") or item.get("9")
                    uemail = uemail or item.get("5")
                    ulogin = ulogin or item.get("9") or item.get("1")

                user_info = {
                    "id": uid,
                    "name": uname,
                    "login": ulogin,
                    "email": uemail,
                }
            elif isinstance(item, list):
                # Tentativa best-effort: identificar posições comuns
                # id geralmente primeiro, name segundo, email pode vir em outra posição
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

def criar_ticket_glpi(dados):
    """Cria ticket no GLPI"""
    try:
        logger.info(f"=== INICIANDO CRIAÇÃO DE TICKET NO GLPI ===")
        logger.info(f"Dados recebidos: {dados}")
        
        # Autentica no GLPI
        logger.info("Iniciando autenticação no GLPI...")
        headers = autenticar_glpi()
        logger.info(f"Headers de autenticação: {headers}")
        
        # Mapeia impacto e urgência
        impact_raw = dados.get("impact", "MEDIO").upper()
        urgency_raw = dados.get("urgency", "MEDIA").upper()
        impact = IMPACT_MAP.get(impact_raw, 2)
        urgency = URGENCY_MAP.get(urgency_raw, 2)
        logger.info(f"Mapeamento - Impact: {impact_raw} -> {impact}, Urgency: {urgency_raw} -> {urgency}")
        
        # Calcula prioridade baseada em impacto e urgência
        priority = min(5, max(1, (impact + urgency) // 2))
        logger.info(f"Prioridade calculada: {priority}")
        
        # Mapeia categoria user-friendly para ID GLPI
        category_raw = dados.get("category")
        category_id = mapear_categoria(category_raw)
        logger.info(f"Mapeamento categoria: {category_raw} -> {category_id}")
        
        # Monta o conteúdo completo
        content_parts = [dados.get("description", "")]
        
        if dados.get("location"):
            content_parts.append(f"Local: {dados['location']}")
        if dados.get("contact_phone"):
            content_parts.append(f"Telefone: {dados['contact_phone']}")
        if dados.get("category"):
            content_parts.append(f"Categoria: {dados['category']}")
            
        content = "\\n\\n".join(filter(None, content_parts))
        logger.info(f"Conteúdo montado: {content}")
        
        # Monta payload para o GLPI
        payload = {
            "input": {
                "name": dados.get("title", "Chamado via Copilot Studio"),
                "content": content,
                "itilcategories_id": category_id,  # ID da categoria GLPI
                "type": 1,  # Incidente
                "urgency": urgency,
                "impact": impact,
                "priority": priority,
                "status": 2,  # Novo
                "entities_id": 1
            }
        }

        # Se houver usuário do requerente resolvido via e-mail, adiciona no payload
        requester_user_id = dados.get("users_id_recipient")
        if requester_user_id:
            payload["input"]["users_id_recipient"] = requester_user_id

        # Campo correto para definir o requerente no GLPI (ator tipo Requester)
        # Referência: API GLPI requer chave com underscore _users_id_requester
        requester_actor_id = dados.get("users_id_requester") or dados.get("users_id_recipient")
        if requester_actor_id:
            payload["input"]["_users_id_requester"] = requester_actor_id
        
        logger.info(f"=== PAYLOAD COMPLETO PARA GLPI ===")
        logger.info(f"Payload: {payload}")
        
        # Envia para o GLPI com encoding UTF-8 explícito
        import json
        payload_json = json.dumps(payload, ensure_ascii=False)
        logger.info(f"Payload JSON: {payload_json}")
        
        # Atualiza headers para incluir charset UTF-8
        headers_with_charset = headers.copy()
        headers_with_charset["Content-Type"] = "application/json; charset=utf-8"
        logger.info(f"Headers finais: {headers_with_charset}")
        
        url_completa = f"{GLPI_URL}/Ticket"
        logger.info(f"URL da requisição: {url_completa}")
        
        logger.info("=== ENVIANDO REQUISIÇÃO PARA GLPI ===")
        response = requests.post(
            url_completa,
            headers=headers_with_charset,
            data=payload_json.encode('utf-8'),
            timeout=10
        )
        
        logger.info(f"=== RESPOSTA DO GLPI ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers da resposta: {dict(response.headers)}")
        logger.info(f"Conteúdo da resposta: {response.text}")
        
        if response.status_code != 201:
            logger.error(f"GLPI retornou status {response.status_code} em vez de 201")
            logger.error(f"Resposta completa: {response.text}")
            raise RuntimeError(f"GLPI retornou status {response.status_code}: {response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        ticket_id = result.get("id")
        
        if not ticket_id:
            logger.error(f"ID do ticket não encontrado na resposta: {result}")
            raise RuntimeError("ID do ticket não retornado pelo GLPI")
            
        logger.info(f"=== TICKET CRIADO COM SUCESSO ===")
        logger.info(f"ID do ticket: {ticket_id}")
        return ticket_id
        
    except Exception as e:
        logger.error(f"=== ERRO NA CRIAÇÃO DO TICKET ===")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem do erro: {str(e)}")
        logger.error(f"Dados que causaram o erro: {dados}")
        raise

@app.route("/", methods=["GET"])
def index():
    """Página inicial"""
    return jsonify({
        "service": "Agente Copilot Studio - GLPI",
        "status": "ativo",
        "version": "1.0",
        "endpoints": {
            "health": "/api/health",
            "create_ticket": "/api/create-ticket-complete",
            "user_by_email": "/api/glpi-user-by-email"
        }
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    """Verifica a saúde da aplicação"""
    try:
        # Verifica configurações
        config_ok = all([GLPI_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN])
        
        status = {
            "status": "ok" if config_ok else "error",
            "glpi_configured": config_ok,
            "timestamp": str(uuid.uuid4())
        }
        
        # Testa conexão com GLPI se configurado
        if config_ok:
            try:
                autenticar_glpi()
                status["glpi_connection"] = "ok"
            except Exception as e:
                status["glpi_connection"] = "error"
                status["glpi_error"] = str(e)
                status["status"] = "warning"
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/api/glpi-user-by-email", methods=["GET"])
def glpi_user_by_email():
    """Busca usuário do GLPI por e-mail (GET ?email=)."""
    try:
        email = request.args.get("email") or request.args.get("e") or request.args.get("mail")
        if not email or "@" not in email:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Parâmetro 'email' é obrigatório",
                "erro": "Parâmetro 'email' é obrigatório"
            }), 400

        # Tenta buscar usuário
        result = buscar_usuario_por_email(email)
        return jsonify({
            "sucesso": True,
            "success": True,
            "query_email": email,
            "resultado": result
        }), 200

    except Exception as e:
        logger.error(f"Erro no lookup de usuário por e-mail: {str(e)}")
        return jsonify({
            "sucesso": False,
            "success": False,
            "error": str(e),
            "erro": str(e)
        }), 500

@app.route("/api/create-ticket-complete", methods=["POST"])
def create_ticket_complete():
    """
    Endpoint para criação de tickets via Copilot Studio
    
    Recebe dados JSON do Copilot Studio e cria um ticket no GLPI.
    Inclui validações de dados e tratamento de expressões PowerFx não processadas.
    
    Returns:
        JSON: Resposta com status da criação do ticket
    """
    trace_id = str(uuid.uuid4())[:8]
    
    try:
        logger.info(f"[{trace_id}] === INICIANDO CREATE_TICKET_COMPLETE ===")
        # Logs detalhados apenas em nível debug para evitar ruído em produção
        logger.debug(f"[{trace_id}] Content-Type: {request.content_type}")
        logger.debug(f"[{trace_id}] Headers: {dict(request.headers)}")
        logger.debug(f"[{trace_id}] Raw data: {request.get_data()}")

        # ========== VALIDAÇÃO JSON MELHORADA ==========
        
        # 1. Verificar Content-Type
        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            logger.warning(f"[{trace_id}] Content-Type incorreto: {content_type}")
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Content-Type deve ser 'application/json'",
                "erro": "Content-Type deve ser 'application/json'",
                "details": {
                    "received_content_type": content_type,
                    "expected_content_type": "application/json"
                },
                "trace_id": trace_id
            }), 400
        
        # 2. Verificar se há dados no corpo
        raw_data = request.get_data()
        if not raw_data:
            logger.error(f"[{trace_id}] Corpo da requisição vazio")
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Corpo da requisição vazio",
                "erro": "Corpo da requisição vazio",
                "trace_id": trace_id
            }), 400
        
        # 3. Tentar parsear JSON com tratamento de erro detalhado
        try:
            data = request.get_json(force=True, silent=False)
        except Exception as json_error:
            logger.error(f"[{trace_id}] Erro ao parsear JSON: {str(json_error)}")
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": f"JSON malformado: {str(json_error)}",
                "erro": f"JSON malformado: {str(json_error)}",
                "details": {
                    "raw_data_preview": raw_data.decode('utf-8', errors='ignore')[:200] + "..." if len(raw_data) > 200 else raw_data.decode('utf-8', errors='ignore')
                },
                "trace_id": trace_id
            }), 400
        
        # 4. Verificar se o JSON foi parseado corretamente
        if data is None:
            logger.error(f"[{trace_id}] JSON parseado como None")
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "JSON resultou em valor nulo",
                "erro": "JSON resultou em valor nulo",
                "trace_id": trace_id
            }), 400
        
        # 5. Verificar se é um dicionário válido
        if not isinstance(data, dict):
            logger.error(f"[{trace_id}] JSON não é um objeto válido: {type(data)}")
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": f"JSON deve ser um objeto, recebido: {type(data).__name__}",
                "erro": f"JSON deve ser um objeto, recebido: {type(data).__name__}",
                "trace_id": trace_id
            }), 400
        
        logger.debug(f"[{trace_id}] Dados recebidos via get_json: {data}")
        
        # Validação básica de dados
        if not data:
            logger.error(f"[{trace_id}] ERRO: Dados JSON não fornecidos")
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Dados JSON não fornecidos",
                "erro": "Dados JSON não fornecidos",
                "trace_id": trace_id
            }), 400
        
        def is_powerfx_expression(value):
            """
            Detecta expressões PowerFx não processadas vindas do Copilot Studio.

            Casos tratados:
            - Sintaxe com chaves: "{Topic.campo}" (alguns editores inserem chaves)
            - Sintaxe com sinal de igual: "=Topic.campo" (Copilot Studio/PowerFx)
            - Sintaxe com marcador inline: "@{Topic.campo}" (variações do editor)
            """
            if isinstance(value, str):
                v = value.strip()
                patterns = [
                    (v.startswith('{') and v.endswith('}') and 'Topic.' in v),
                    (v.startswith('=') and 'Topic.' in v),
                    (v.startswith('@{') and v.endswith('}') and 'Topic.' in v),
                ]
                return any(patterns)
            return False

        # Verifica se há expressões PowerFx não processadas
        logger.info(f"[{trace_id}] Verificando expressões PowerFx não processadas...")
        powerfx_fields = []
        for key, value in data.items():
            logger.info(f"[{trace_id}] Verificando campo {key}: {value}")
            if is_powerfx_expression(value):
                logger.info(f"[{trace_id}] Campo PowerFx detectado: {key}: {value}")
                powerfx_fields.append(f"{key}: {value}")
        
        logger.info(f"[{trace_id}] Campos PowerFx encontrados: {powerfx_fields}")
        if powerfx_fields:
            error_response = {
                "sucesso": False,
                "success": False,
                "error": "Expressões PowerFx não processadas detectadas",
                "erro": "O Copilot Studio não processou as expressões PowerFx corretamente. Verifique a configuração do agente.",
                "details": {
                    "unprocessed_fields": powerfx_fields,
                    "suggestion": "Verifique se as variáveis Topic estão sendo definidas corretamente no Copilot Studio"
                },
                "trace_id": trace_id
            }
            logger.info(f"[{trace_id}] Retornando erro PowerFx: {error_response}")
            return jsonify(error_response), 400
        
        # Normaliza campos para aceitar português e inglês
        description = data.get('description') or data.get('descricao')
        title = data.get('title') or data.get('titulo')
        category = data.get('category') or data.get('categoria')
        impact = data.get('impact') or data.get('impacto')
        location = data.get('location') or data.get('localizacao')
        contact_phone = data.get('contact_phone') or data.get('telefone_contato') or data.get('telefone')
        requester_email = data.get('requester_email') or data.get('email') or data.get('usuario_email')
        
        # Mapeia categoria user-friendly para categoria GLPI
        glpi_category = mapear_categoria(category)
        logger.info(f"[{trace_id}] Categoria original: {category} -> Categoria GLPI: {glpi_category}")
        
        # Normaliza dados para formato padrão
        normalized_data = {
            'description': description,
            'title': title,
            'category': glpi_category,
            'category_user_friendly': category,  # Mantém categoria original para logs
            'impact': impact,
            'location': location,
            'contact_phone': contact_phone,
            'requester_email': requester_email
        }

        # ========== VALIDAÇÕES DA FASE 1 - BACKUP NO BACKEND ==========

        # Validação 1: Descrição obrigatória e tamanho mínimo considerando conteúdo completo
        if not description:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Campo 'description/descricao' é obrigatório",
                "erro": "Campo 'description/descricao' é obrigatório",
                "trace_id": trace_id
            }), 400
        
        # Monta conteúdo similar ao que será enviado ao GLPI para validar tamanho
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
                "erro": "O conteúdo total do chamado está curto. Inclua mais detalhes na descrição ou informe local, telefone e categoria para complementar.",
                "details": {
                    "current_length": len(full_content_validate.strip()),
                    "required_length": 50
                },
                "trace_id": trace_id
            }), 400
            
        # Validação 2: Detecção de palavras vagas na descrição
        vague_words = ['problema', 'erro', 'não funciona', 'quebrado', 'ruim', 'lento', 'travando', 'bug']
        description_lower = description.lower()
        found_vague_words = [word for word in vague_words if word in description_lower]
        
        if found_vague_words and len(full_content_validate.strip()) < 100:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Descrição muito vaga",
                "erro": f"Sua descrição contém termos genéricos: {', '.join(found_vague_words)}. Por favor, seja mais específico sobre o que exatamente está acontecendo.",
                "suggestions": [
                    "Descreva os passos que levaram ao problema",
                    "Inclua mensagens de erro específicas",
                    "Mencione quando o problema começou",
                    "Detalhe o comportamento esperado vs atual"
                ],
                "trace_id": trace_id
            }), 400
            
        # Validação 3: Telefone obrigatório e formato mínimo
        if not contact_phone or len(contact_phone.strip()) < 8:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Telefone inválido",
                "erro": "O telefone de contato é obrigatório e deve ter pelo menos 8 dígitos.",
                "details": {
                    "current_phone": contact_phone or "vazio"
                },
                "trace_id": trace_id
            }), 400
            
        if not title:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Campo 'title/titulo' é obrigatório",
                "erro": "Campo 'title/titulo' é obrigatório",
                "trace_id": trace_id
            }), 400
            
        if not category:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Campo 'category/categoria' é obrigatório",
                "erro": "Campo 'category/categoria' é obrigatório",
                "trace_id": trace_id
            }), 400
            
        if not impact:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Campo 'impact/impacto' é obrigatório",
                "erro": "Campo 'impact/impacto' é obrigatório",
                "trace_id": trace_id
            }), 400
            
        # Validação 4: Localização obrigatória e formato mínimo
        if not location or len(location.strip()) < 3:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Localização inválida",
                "erro": "A localização é obrigatória e deve ter pelo menos 3 caracteres.",
                "details": {
                    "current_location": location or "vazio"
                },
                "trace_id": trace_id
            }), 400
        
        # Verifica configurações do GLPI
        if not all([GLPI_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN]):
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Configurações do GLPI não encontradas. Verifique o arquivo .env",
                "erro": "Configurações do GLPI não encontradas. Verifique o arquivo .env",
                "trace_id": trace_id
            }), 500
        
        # Se houver e-mail do requerente, tenta resolver usuário no GLPI
        requester_lookup = None
        if requester_email:
            try:
                requester_lookup = buscar_usuario_por_email(requester_email)
                if requester_lookup.get("found") and requester_lookup.get("user_id"):
                    # Define tanto recipient quanto requester para máxima compatibilidade
                    normalized_data["users_id_recipient"] = requester_lookup["user_id"]
                    normalized_data["users_id_requester"] = requester_lookup["user_id"]
            except Exception as e:
                logger.warning(f"[{trace_id}] Falha ao buscar usuário por e-mail '{requester_email}': {e}")

        # Cria ticket no GLPI
        ticket_id = criar_ticket_glpi(normalized_data)
        
        logger.info(f"[{trace_id}] Ticket {ticket_id} criado com sucesso")
        
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
                    "login": requester_lookup.get("login") if requester_lookup else None
                } if requester_email else None
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{trace_id}] Erro ao criar ticket: {error_msg}")
        
        return jsonify({
            "sucesso": False,
            "success": False,
            "error": error_msg,
            "erro": error_msg,
            "trace_id": trace_id
        }), 500

if __name__ == "__main__":
    logger.info("Iniciando Agente Copilot Studio - GLPI")
    logger.info(f"GLPI URL: {GLPI_URL}")
    logger.info(f"GLPI configurado: {bool(GLPI_URL and GLPI_APP_TOKEN and GLPI_USER_TOKEN)}")
    
    # Configurações para produção
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no servidor: {e}")
        raise
