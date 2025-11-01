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
        return 1  # ID da categoria padrão
    
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
    return 1

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

def criar_ticket_glpi(dados):
    """Cria ticket no GLPI"""
    try:
        # Autentica no GLPI
        headers = autenticar_glpi()
        
        # Mapeia impacto e urgência
        impact = IMPACT_MAP.get(dados.get("impact", "MEDIO").upper(), 2)
        urgency = URGENCY_MAP.get(dados.get("urgency", "MEDIA").upper(), 2)
        
        # Calcula prioridade baseada em impacto e urgência
        priority = min(5, max(1, (impact + urgency) // 2))
        
        # Mapeia categoria user-friendly para ID GLPI
        category_id = mapear_categoria(dados.get("category"))
        
        # Monta o conteúdo completo
        content_parts = [dados.get("description", "")]
        
        if dados.get("location"):
            content_parts.append(f"Local: {dados['location']}")
        if dados.get("contact_phone"):
            content_parts.append(f"Telefone: {dados['contact_phone']}")
        if dados.get("category"):
            content_parts.append(f"Categoria: {dados['category']}")
            
        content = "\\n\\n".join(filter(None, content_parts))
        
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
        
        logger.info(f"Payload enviado ao GLPI: {payload}")
        
        # Envia para o GLPI com encoding UTF-8 explícito
        import json
        payload_json = json.dumps(payload, ensure_ascii=False)
        
        # Atualiza headers para incluir charset UTF-8
        headers_with_charset = headers.copy()
        headers_with_charset["Content-Type"] = "application/json; charset=utf-8"
        
        response = requests.post(
            f"{GLPI_URL}/Ticket",
            headers=headers_with_charset,
            data=payload_json.encode('utf-8'),
            timeout=10
        )
        
        logger.info(f"Status da resposta GLPI: {response.status_code}")
        logger.info(f"Resposta GLPI: {response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        ticket_id = result.get("id")
        
        if not ticket_id:
            raise RuntimeError("ID do ticket não retornado pelo GLPI")
            
        return ticket_id
        
    except Exception as e:
        logger.error(f"Erro ao criar ticket no GLPI: {str(e)}")
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
            "create_ticket": "/api/create-ticket-complete"
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

@app.route("/api/create-ticket-complete", methods=["POST"])
def create_ticket_complete():
    """
    Endpoint para criação de tickets via Copilot Studio
    
    Recebe dados JSON do Copilot Studio e cria um ticket no GLPI.
    Inclui validações de dados e tratamento de expressões PowerFx não processadas.
    
    Returns:
        JSON: Resposta com status da criação do ticket
    """
    trace_id = str(uuid.uuid4())
    
    try:
        # Processa dados JSON da requisição
        data = request.get_json(force=True)
        logger.info(f"[{trace_id}] Dados recebidos: {data}")
        
        # Validação básica de dados
        if not data:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Dados JSON não fornecidos",
                "erro": "Dados JSON não fornecidos",
                "trace_id": trace_id
            }), 400
        
        def is_powerfx_expression(value):
            """
            Detecta expressões PowerFx não processadas
            
            Args:
                value: Valor a ser verificado
                
            Returns:
                bool: True se for uma expressão PowerFx não processada
            """
            if isinstance(value, str):
                return (value.startswith('{') and 
                       value.endswith('}') and 
                       'Topic.' in value)
            return False

        # Verifica se há expressões PowerFx não processadas
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
                    "suggestion": "Verifique se as variáveis Topic estão sendo definidas corretamente no Copilot Studio"
                },
                "trace_id": trace_id
            }), 400
        
        # Normaliza campos para aceitar português e inglês
        description = data.get('description') or data.get('descricao')
        title = data.get('title') or data.get('titulo')
        category = data.get('category') or data.get('categoria')
        impact = data.get('impact') or data.get('impacto')
        location = data.get('location') or data.get('localizacao')
        contact_phone = data.get('contact_phone') or data.get('telefone_contato') or data.get('telefone')
        
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
            'contact_phone': contact_phone
        }
        
        # ========== VALIDAÇÕES DA FASE 1 - BACKUP NO BACKEND ==========
        
        # Validação 1: Descrição obrigatória e tamanho mínimo
        if not description:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Campo 'description/descricao' é obrigatório",
                "erro": "Campo 'description/descricao' é obrigatório",
                "trace_id": trace_id
            }), 400
            
        if len(description.strip()) < 50:
            return jsonify({
                "sucesso": False,
                "success": False,
                "error": "Descrição muito curta",
                "erro": "A descrição deve ter pelo menos 50 caracteres. Forneça mais detalhes sobre o problema.",
                "details": {
                    "current_length": len(description.strip()),
                    "required_length": 50
                },
                "trace_id": trace_id
            }), 400
            
        # Validação 2: Detecção de palavras vagas na descrição
        vague_words = ['problema', 'erro', 'não funciona', 'quebrado', 'ruim', 'lento', 'travando', 'bug']
        description_lower = description.lower()
        found_vague_words = [word for word in vague_words if word in description_lower]
        
        if found_vague_words and len(description.strip()) < 100:
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
                "location": location
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