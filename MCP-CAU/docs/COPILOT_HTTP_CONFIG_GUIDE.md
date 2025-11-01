# Guia de Configuração HTTP para Copilot Studio

## Visão Geral

Este guia explica detalhadamente como configurar requisições HTTP em tópicos do Microsoft Copilot Studio, baseado na documentação oficial e nas melhores práticas.

## Estrutura do HttpRequestAction

### Parâmetros Obrigatórios

#### 1. **kind**: HttpRequestAction
- Define o tipo de ação como requisição HTTP
- Valor fixo: `HttpRequestAction`

#### 2. **id**: Identificador único
- Identificador único para a ação dentro do tópico
- Exemplo: `checkApiHealth`, `createTicket`

#### 3. **url**: URL do endpoint
- URL completa do endpoint da API
- Pode usar variáveis: `"${Topic.BaseUrl}/api/tickets"`
- Exemplo: `"http://localhost:5000/api/model-health"`

#### 4. **method**: Método HTTP
- Métodos suportados: GET, POST, PUT, PATCH, DELETE
- Exemplo: `GET`, `POST`

### Parâmetros Opcionais

#### 5. **headers**: Cabeçalhos HTTP
```yaml
headers:
  Content-Type: "application/json"
  Accept: "application/json"
  Authorization: "Bearer ${Topic.AuthToken}"
```

#### 6. **body**: Corpo da requisição (para POST/PUT)
```yaml
body:
  contentType: JSON
  content: |
    {
      "text": "${Topic.UserMessage}",
      "category": "${Topic.Category}"
    }
```

#### 7. **timeout**: Timeout em milissegundos
- Padrão: 30000 (30 segundos)
- Máximo recomendado: 120000 (2 minutos)

#### 8. **responseDataType**: Tipo de resposta esperada
- Opções: `JSON`, `Text`, `XML`
- Padrão: `JSON`

#### 9. **saveResponseAs**: Variável para salvar resposta
- Nome da variável onde a resposta será armazenada
- Exemplo: `Topic.ApiResponse`

### Tratamento de Erros

#### 10. **errorHandling**: Configuração de tratamento de erros
```yaml
errorHandling:
  onError: continue  # ou "stop"
  saveStatusCodeAs: Topic.StatusCode
  saveErrorResponseAs: Topic.ErrorResponse
```

## Configurações Específicas para Nosso Projeto

### 1. Endpoint de Health Check
```yaml
- kind: HttpRequestAction
  id: checkApiHealth
  url: "http://localhost:5000/api/model-health"
  method: GET
  headers:
    Accept: "application/json"
  timeout: 30000
  responseDataType: JSON
  saveResponseAs: Topic.HealthResponse
```

### 2. Endpoint de Criação de Tickets
```yaml
- kind: HttpRequestAction
  id: createTicket
  url: "http://localhost:5000/api/create-ticket-from-text"
  method: POST
  headers:
    Content-Type: "application/json"
    Accept: "application/json"
  body:
    contentType: JSON
    content: |
      {
        "text": "${Topic.UserMessage}"
      }
  timeout: 60000
  responseDataType: JSON
  saveResponseAs: Topic.TicketResponse
```

## Variáveis Disponíveis

### Variáveis de Sistema
- `${Topic.UserMessage}`: Mensagem do usuário
- `${Topic.ConversationId}`: ID da conversa
- `${Topic.UserId}`: ID do usuário

### Variáveis Personalizadas
- `${Topic.HealthResponse}`: Resposta do health check
- `${Topic.TicketResponse}`: Resposta da criação do ticket
- `${Topic.StatusCode}`: Código de status HTTP
- `${Topic.ErrorResponse}`: Resposta de erro

## Acessando Dados da Resposta

### Resposta JSON do Health Check
```yaml
# Acessar propriedades da resposta
${Topic.HealthResponse.ok}
${Topic.HealthResponse.ollama_host}
${Topic.HealthResponse.model_status}
```

### Resposta JSON da Criação de Ticket
```yaml
# Acessar propriedades da resposta
${Topic.TicketResponse.success}
${Topic.TicketResponse.ticket_id}
${Topic.TicketResponse.categoria}
${Topic.TicketResponse.prioridade}
${Topic.TicketResponse.trace_id}
```

## Configuração no Copilot Studio (Interface)

### 1. Configuração Básica
- **URL**: `http://localhost:5000/api/create-ticket-from-text`
- **Método**: `POST`

### 2. Cabeçalhos
- **Chave**: `Content-Type`, **Valor**: `application/json`
- **Chave**: `Accept`, **Valor**: `application/json`

### 3. Corpo da Requisição
- **Tipo**: `Conteúdo JSON`
- **Conteúdo**:
```json
{
  "text": "Preciso de ajuda com meu computador"
}
```

### 4. Tipo de Dados de Resposta
- Selecionar: `JSON`
- Fornecer exemplo de resposta para gerar esquema

### 5. Salvar Resposta Como
- Nome da variável: `TicketResponse`

### 6. Tratamento de Erros
- Selecionar: `Continuar em caso de erro`
- **Cabeçalhos de resposta**: `ResponseHeaders`
- **Código de status**: `StatusCode`
- **Resposta de erro**: `ErrorResponse`

## Exemplo de Resposta JSON para Configuração

### Resposta de Sucesso
```json
{
  "success": true,
  "ticket_id": "12345",
  "categoria": "Suporte Técnico",
  "prioridade": "Média",
  "confianca": 0.85,
  "trace_id": "abc123def",
  "model_used": "llama3.1:8b"
}
```

### Resposta de Erro
```json
{
  "success": false,
  "error": "Texto vazio",
  "trace_id": "abc123def"
}
```

## Dicas de Implementação

1. **Teste Gradual**: Comece com o endpoint de health check antes de implementar a criação de tickets
2. **Timeout Adequado**: Use timeouts maiores para operações que envolvem IA
3. **Tratamento de Erros**: Sempre configure tratamento de erros para melhor experiência do usuário
4. **Variáveis Dinâmicas**: Use variáveis do Power Fx para tornar as requisições dinâmicas
5. **Logs**: Monitore os logs da aplicação Flask para debug

## Próximos Passos

1. Importe o YAML no Copilot Studio
2. Teste o endpoint de health check primeiro
3. Configure as variáveis de ambiente necessárias
4. Teste a criação de tickets
5. Ajuste o tratamento de respostas conforme necessário