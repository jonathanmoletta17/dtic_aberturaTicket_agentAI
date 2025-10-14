# app.py
import os, re, json, uuid, logging
from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_form_schemas():
    """Carrega os schemas de formulários do arquivo JSON"""
    try:
        # Usa caminho absoluto baseado na localização do script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(script_dir, "config", "form_schemas.json")
        
        with open(schema_path, "r", encoding="utf-8") as f:
            schemas = json.load(f)
            logger.info(f"Schemas carregados com sucesso: {len(schemas.get('categories', []))} categorias")
            return schemas
    except Exception as e:
        logger.error(f"Erro ao carregar form_schemas.json: {e}")
        return {"categories": []}

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Configurações do GLPI
API_URL = os.getenv("API_URL")
APP_TOKEN = os.getenv("APP_TOKEN")
USER_TOKEN = os.getenv("USER_TOKEN")

def authenticate_glpi():
    """Autentica no GLPI e retorna headers com session token"""
    if not all([API_URL, APP_TOKEN, USER_TOKEN]):
        raise RuntimeError("Configurações do GLPI não encontradas no .env")
    
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        resp = requests.post(f"{API_URL}/initSession", headers=headers, timeout=(5, 10))
        resp.raise_for_status()
        data = resp.json()
        session_token = data.get("session_token")
        
        if not session_token:
            raise RuntimeError("GLPI: session_token ausente na resposta de initSession")
        
        return {
            "App-Token": APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json"
        }
    except Exception as e:
        print(f"Erro na autenticação GLPI: {e}")
        raise

def glpi_post(endpoint, data):
    """Faz POST para o GLPI com autenticação"""
    try:
        headers = authenticate_glpi()
        url = f"{API_URL}{endpoint}"
        
        resp = requests.post(url, headers=headers, json=data, timeout=(5, 30))
        resp.raise_for_status()
        
        return resp.json()
    except Exception as e:
        print(f"Erro ao criar ticket no GLPI: {e}")
        raise

ROUTING = {
    "INSTALACAO": 15,
    "ATOLAMENTO": 57,
    "TROCA_TONNER": 71,
    "MOVIMENTACAO_FISICA": 72,
}

def infer_priority(text: str) -> int:
    t = text.lower()
    if any(w in t for w in ["urgente","crítico","parado","emergência"]): return 5
    if any(w in t for w in ["importante","alta"]): return 4
    return 3

def sanitize_ramal(r: str) -> str:
    m = re.findall(r"\b(\d{3,6})\b", r or "")
    return m[0] if m else ""

def call_ollama_extract(user_text: str, trace_id: str = None) -> dict:
    """Extrai informações usando o novo prompt multicategoria"""
    if not trace_id:
        trace_id = str(uuid.uuid4())[:8]
    
    # Carrega schemas dinâmicos
    schemas = load_form_schemas()
    
    # Carrega o novo prompt multicategoria
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        prompt_path = os.path.join(script_dir, "prompt_extracao_multicategoria.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        logger.error(f"[{trace_id}] Arquivo prompt_extracao_multicategoria.txt não encontrado")
        # Fallback para o prompt antigo
        prompt_path_old = os.path.join(script_dir, "prompt_extracao.txt")
        with open(prompt_path_old, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    
    # Substitui placeholders
    prompt = prompt_template.replace("{SCHEMAS_JSON_AQUI}", json.dumps(schemas, indent=2, ensure_ascii=False))
    prompt = prompt.replace("{mensagem_livre_do_usuario}", user_text)
    
    logger.info(f"[{trace_id}] Iniciando extração para texto: {user_text[:100]}...")
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "temperature": 0.0,  # Determinístico conforme especificação
        "format": "json",
        "stream": False
    }
    
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60)
        r.raise_for_status()
        
        data = r.json()
        if "response" in data:
            result = json.loads(data["response"])
            logger.info(f"[{trace_id}] Extração concluída - Categoria: {result.get('categoria', 'N/A')}")
            return result
        
        logger.error(f"[{trace_id}] Resposta do Ollama sem campo 'response'")
        return {}
        
    except Exception as e:
        logger.error(f"[{trace_id}] Erro na extração: {e}")
        return {}

def build_ticket_state(extract: dict, user_text: str, trace_id: str = None) -> dict:
    """Constrói o estado do ticket a partir da extração multicategoria"""
    if not trace_id:
        trace_id = str(uuid.uuid4())[:8]
    
    # Extrai dados da nova estrutura multicategoria
    categoria = extract.get("categoria", "INCIDENTE")
    campos = extract.get("campos", {})
    faltantes = extract.get("faltantes", [])
    prioridade = extract.get("prioridade", "MEDIA")
    payload_glpi = extract.get("payload_glpi", {})
    
    # Mapeia prioridade para valores numéricos
    priority_map = {"BAIXA": 2, "MEDIA": 3, "ALTA": 5}
    priority_num = priority_map.get(prioridade, 3)
    
    # Constrói título se não fornecido
    titulo = payload_glpi.get("titulo") or f"[AUTO] {categoria}"
    if campos.get("location"):
        titulo += f" - {campos['location']}"
    
    # Constrói descrição consolidada
    descricao = payload_glpi.get("descricao") or campos.get("description") or user_text.strip()
    
    # Adiciona ramal à descrição se presente
    ramal = sanitize_ramal(campos.get("contact_phone", ""))
    if ramal:
        descricao += f"\n\nRamal: {ramal}"
    
    state = {
        "categoria": categoria,
        "campos": campos,
        "faltantes": faltantes,
        "prioridade": prioridade,
        "titulo": titulo,
        "descricao": descricao,
        "ramal": ramal,
        "localizacao": campos.get("location", ""),
        "routing_id": None,  # Será definido dinamicamente
        "priority": priority_num,
        "urgency": 3,
        "impact": 3,
        "payload_glpi": payload_glpi,
        "confianca_categoria": extract.get("confianca_categoria", 0.0),
        "motivos_prioridade": extract.get("motivos_prioridade", []),
        "ui_form": extract.get("ui_form", {})
    }
    
    logger.info(f"[{trace_id}] Estado do ticket construído - Categoria: {categoria}, Faltantes: {faltantes}")
    return state

def get_routing_id(categoria: str, campos: dict) -> int:
    """Determina o routing_id baseado na categoria e campos"""
    schemas = load_form_schemas()
    
    # Busca a categoria nos schemas
    for cat in schemas.get("categories", []):
        if cat["slug"] == categoria:
            routing = cat.get("routing", {})
            
            # Para categorias com múltiplas opções de roteamento
            if len(routing) > 1:
                # Tenta encontrar baseado nos campos
                for field in cat.get("fields", []):
                    if field["name"] in campos and field.get("type") == "enum":
                        field_value = campos[field["name"]]
                        if field_value in routing:
                            return routing[field_value]
                
                # Se não encontrou, usa o primeiro disponível
                return list(routing.values())[0]
            
            # Para categorias com roteamento único
            elif routing:
                return list(routing.values())[0]
    
    # Fallback para categoria INCIDENTE
    return 7

def build_glpi_payload(state: dict, trace_id: str = None) -> dict:
    """Constrói o payload para o GLPI baseado no estado multicategoria"""
    if not trace_id:
        trace_id = str(uuid.uuid4())[:8]
    
    categoria = state["categoria"]
    campos = state["campos"]
    
    # Determina routing_id dinamicamente
    routing_id = get_routing_id(categoria, campos)
    
    # Busca itilcategories_id nos schemas
    schemas = load_form_schemas()
    itilcategories_id = 7  # Default para INCIDENTE
    
    for cat in schemas.get("categories", []):
        if cat["slug"] == categoria:
            itilcategories_id = cat.get("itilcategories_id", 7)
            break
    
    # Constrói campos customizados do formcreator
    formcreator_fields = {}
    for field_name, field_value in campos.items():
        if field_value:  # Só inclui campos preenchidos
            formcreator_fields[f"formcreator_field_{field_name}"] = field_value
    
    payload = {
        "name": state["titulo"],
        "content": state["descricao"],
        "itilcategories_id": itilcategories_id,
        "urgency": state["urgency"],
        "impact": state["impact"],
        "priority": state["priority"],
        "plugin_formcreator_forms_id": routing_id,
        "_plugin_formcreator_fields": formcreator_fields
    }
    
    logger.info(f"[{trace_id}] Payload GLPI construído - Categoria: {categoria}, Routing ID: {routing_id}")
    return payload

@app.route("/api/model-health", methods=["GET"])
def model_health():
    try:
        test = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": "Responda em JSON: {\"ok\": true}",
            "temperature": 0,
            "format": "json",
            "stream": False
        }, timeout=20).json()
        return jsonify({
            "ok": True,
            "ollama_host": OLLAMA_HOST,
            "model": OLLAMA_MODEL,
            "raw": test.get("response","")
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "ollama_host": OLLAMA_HOST, "model": OLLAMA_MODEL}), 500

@app.route("/api/create-ticket-from-text", methods=["POST"])
def create_ticket_from_text():
    # Gera trace_id para rastreamento
    trace_id = str(uuid.uuid4())[:8]
    
    # Aceita tanto JSON quanto text/plain
    if request.content_type == 'text/plain':
        user_text = request.get_data(as_text=True).strip()
    else:
        payload = request.get_json(force=True)
        user_text = (payload or {}).get("text","").strip()
    
    logger.info(f"[{trace_id}] Nova requisição de criação de ticket")
    
    if not user_text:
        logger.warning(f"[{trace_id}] Texto vazio recebido")
        return jsonify({"success": False, "error": "texto vazio"}), 400

    # 1) Extrai com Ollama usando novo sistema multicategoria
    try:
        extract = call_ollama_extract(user_text, trace_id)
        logger.info(f"[{trace_id}] Extração concluída: {extract.get('categoria', 'N/A')}")
    except Exception as e:
        logger.error(f"[{trace_id}] Erro no Ollama: {str(e)}")
        return jsonify({"success": False, "error": f"Erro no Ollama: {str(e)}"}), 500

    # 2) Consolida estado multicategoria
    state = build_ticket_state(extract, user_text, trace_id)
    
    # 3) Verifica campos faltantes baseado na categoria
    faltantes = state.get("faltantes", [])
    
    if faltantes:
        logger.info(f"[{trace_id}] Campos faltantes: {faltantes}")
        return jsonify({
            "success": False,
            "need": faltantes,
            "message": f"Faltam campos obrigatórios para categoria {state['categoria']}",
            "preview": state,
            "categoria": state["categoria"],
            "confianca": state.get("confianca_categoria", 0.0),
            "ui_form": state.get("ui_form", {}),
            "trace_id": trace_id
        }), 200

    # 4) Constrói payload para GLPI
    glpi_payload = build_glpi_payload(state, trace_id)

    # 5) Envia ao GLPI (criação real do ticket)
    try:
        resp = glpi_post("/Ticket", {"input": glpi_payload})
        ticket_id = resp.get("id")
        
        if not ticket_id:
            logger.error(f"[{trace_id}] GLPI não retornou ID do ticket")
            return jsonify({
                "success": False,
                "error": "GLPI não retornou ID do ticket",
                "preview": state,
                "payload": glpi_payload,
                "model_used": OLLAMA_MODEL,
                "trace_id": trace_id
            }), 500
        
        logger.info(f"[{trace_id}] Ticket criado com sucesso - ID: {ticket_id}")
        return jsonify({
            "success": True,
            "ticket_id": ticket_id,
            "preview": state,
            "payload": glpi_payload,
            "model_used": OLLAMA_MODEL,
            "categoria": state["categoria"],
            "confianca": state.get("confianca_categoria", 0.0),
            "prioridade": state["prioridade"],
            "motivos_prioridade": state.get("motivos_prioridade", []),
            "trace_id": trace_id
        }), 201
        
    except Exception as e:
        logger.error(f"[{trace_id}] Erro ao criar ticket: {e}")
        return jsonify({
            "success": False,
            "error": f"Erro ao criar ticket no GLPI: {str(e)}",
            "preview": state,
            "payload": glpi_payload,
            "model_used": OLLAMA_MODEL,
            "trace_id": trace_id
        }), 500

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)