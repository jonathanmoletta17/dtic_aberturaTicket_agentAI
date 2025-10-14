import json
import requests
import sys
import os

# Adiciona o diretório MCP-CAU ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'MCP-CAU'))

from app import load_form_schemas

def test_llm_response():
    # Carrega schemas
    schemas = load_form_schemas()
    
    # Carrega o prompt
    with open("MCP-CAU/prompt_extracao_multicategoria.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()
    
    # Texto de teste
    user_text = "O computador da recepcao esta muito lento e travando constantemente. Impacta o atendimento aos clientes. Ramal: 4248"
    
    # Substitui placeholders
    prompt = prompt_template.replace("{SCHEMAS_JSON_AQUI}", json.dumps(schemas, indent=2, ensure_ascii=False))
    prompt = prompt.replace("{mensagem_livre_do_usuario}", user_text)
    
    print("=== PROMPT ENVIADO PARA O LLM ===")
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    print("\n" + "="*50 + "\n")
    
    # Faz requisição para o LLM
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "temperature": 0.0,
        "format": "json",
        "stream": False
    }
    
    try:
        r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        r.raise_for_status()
        
        data = r.json()
        if "response" in data:
            result = json.loads(data["response"])
            print("=== RESPOSTA DO LLM ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n=== ANÁLISE ===")
            print(f"Categoria: {result.get('categoria')}")
            print(f"Campos: {result.get('campos')}")
            print(f"Faltantes: {result.get('faltantes')}")
            
            # Verifica se os campos faltantes são válidos para a categoria
            categoria = result.get('categoria')
            if categoria:
                for cat in schemas.get('categories', []):
                    if cat['slug'] == categoria:
                        campos_validos = [f['name'] for f in cat['fields']]
                        print(f"Campos válidos para {categoria}: {campos_validos}")
                        
                        faltantes = result.get('faltantes', [])
                        campos_invalidos = [f for f in faltantes if f not in campos_validos]
                        if campos_invalidos:
                            print(f"❌ ERRO: Campos inválidos retornados: {campos_invalidos}")
                        else:
                            print("✅ Todos os campos faltantes são válidos")
                        break
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_llm_response()