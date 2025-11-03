# Guia de Resolução de Inconsistências - Sistema GLPI Agent

## 📋 Resumo das Inconsistências Identificadas e Resolvidas

### 🔍 Problemas Identificados

1. **JSON Parsing via Túnel**: JSON como string falhava, mas como byte[] funcionava
2. **Validação Genérica**: Mensagens de erro pouco específicas
3. **Headers Inconsistentes**: Falta de padronização de Content-Type
4. **Logging Limitado**: Dificuldade para rastrear problemas

### ✅ Soluções Implementadas

## 1. Validação JSON Melhorada

### Antes:
```python
data = request.get_json(force=True, silent=True)
if not data:
    return jsonify({"erro": "Erro no formato JSON: corpo ausente ou inválido"})
```

### Depois:
```python
def validate_json_request():
    # Verifica Content-Type
    content_type = request.headers.get('Content-Type', '')
    if not content_type.startswith('application/json'):
        return {
            "erro": "Content-Type deve ser 'application/json'",
            "details": {
                "expected_content_type": "application/json",
                "received_content_type": content_type
            }
        }
    
    # Verifica se há dados
    if not request.data:
        return {"erro": "Corpo da requisição vazio"}
    
    # Tenta fazer parse do JSON
    try:
        data = request.get_json(force=True)
        if data is None or not isinstance(data, dict):
            return {"erro": "JSON deve ser um objeto válido"}
        return {"success": True, "data": data}
    except Exception as e:
        return {
            "erro": f"JSON malformado: {str(e)}",
            "details": {"raw_data_preview": request.data.decode('utf-8')[:50]}
        }
```

## 2. Middleware de Headers Padronizados

```python
@app.before_request
def ensure_json_headers():
    trace_id = str(uuid.uuid4())[:8]
    g.trace_id = trace_id
    
    # Log detalhado da requisição
    logger.info(f"[{trace_id}] {request.method} {request.path}")
    logger.info(f"[{trace_id}] Headers: {dict(request.headers)}")
    
    # Aviso para requisições POST/PUT/PATCH sem Content-Type correto
    if request.method in ['POST', 'PUT', 'PATCH'] and request.data:
        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            logger.warning(f"[{trace_id}] Content-Type incorreto: {content_type}")
```

## 3. Logging Detalhado com Trace ID

- Cada requisição recebe um `trace_id` único
- Logs incluem método, path e headers
- Facilita rastreamento de problemas específicos

## 📊 Resultados dos Testes

### ✅ Testes Realizados e Aprovados

1. **JSON Malformado**:
   ```bash
   curl -X POST "http://localhost:5000/api/create-ticket-complete" \
        -H "Content-Type: application/json" \
        -d "{ invalid json"
   ```
   **Resultado**: Erro específico com preview dos dados

2. **Content-Type Ausente**:
   ```bash
   curl -X POST "http://localhost:5000/api/create-ticket-complete" \
        -d '{"description":"teste"}'
   ```
   **Resultado**: Erro específico sobre Content-Type

3. **Via Túnel com JSON String** (antes falhava):
   ```powershell
   $body = '{"category":"SEGURANCA",...}'
   Invoke-RestMethod -Uri "https://tunnel.../api/create-ticket-complete" \
                     -Method POST -Body $body -ContentType "application/json"
   ```
   **Resultado**: ✅ Sucesso - Ticket #11090 criado

4. **Via Túnel com Byte Array**:
   ```powershell
   $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
   Invoke-RestMethod -Uri "https://tunnel.../api/create-ticket-complete" \
                     -Method POST -Body $bodyBytes -ContentType "application/json; charset=utf-8"
   ```
   **Resultado**: ✅ Sucesso - Ticket #11089 criado

## 🔧 Como Usar as Melhorias

### Para Desenvolvedores

1. **Sempre use Content-Type correto**:
   ```
   Content-Type: application/json
   ```

2. **Para requisições via túnel, prefira**:
   ```
   Content-Type: application/json; charset=utf-8
   ```

3. **Use o trace_id dos logs para debugging**:
   ```
   [fa626776] Ticket 11089 criado com sucesso
   ```

### Para Copilot Studio

O arquivo `copilot-create-ticket-config.tunnel.yaml` já está atualizado com:
- Headers corretos
- URL do túnel ativo
- Tratamento de erros melhorado

## 🚨 Monitoramento

### Logs a Observar

1. **Requisições com problemas**:
   ```
   [trace_id] Content-Type incorreto: application/x-www-form-urlencoded
   ```

2. **JSON malformado**:
   ```
   [trace_id] JSON malformado: 400 Bad Request
   ```

3. **Sucessos**:
   ```
   [trace_id] Ticket XXXXX criado com sucesso
   ```

## 📈 Benefícios Alcançados

1. **Consistência**: JSON string e byte[] funcionam igualmente
2. **Debugging**: Trace IDs facilitam identificação de problemas
3. **Clareza**: Mensagens de erro específicas
4. **Robustez**: Validação em múltiplas camadas
5. **Compatibilidade**: Funciona local e via túnel

## 🔄 Próximos Passos Recomendados

1. **Túnel Nomeado**: Substituir quick tunnel por named tunnel para estabilidade
2. **Testes Automatizados**: Implementar suite de testes para validação contínua
3. **Retry Logic**: Adicionar retry automático para falhas temporárias
4. **Monitoramento**: Implementar alertas para padrões de erro

---

**Status**: ✅ Inconsistências resolvidas e sistema estável
**Data**: 03/11/2025
**Versão**: 1.0