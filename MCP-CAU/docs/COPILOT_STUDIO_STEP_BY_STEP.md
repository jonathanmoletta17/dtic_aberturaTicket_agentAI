# Guia Passo a Passo: Configuração HTTP no Copilot Studio

## 📋 Pré-requisitos

1. ✅ API funcionando em `http://localhost:5000`
2. ✅ Endpoints testados e validados
3. ✅ Copilot Studio aberto com o tópico criado

## 🔧 Configuração da Solicitação HTTP

### Passo 1: Configuração Básica da URL

**Campo: URL** ⭐ (obrigatório)
```
http://localhost:5000/api/create-ticket-from-text
```

**Observações:**
- ⚠️ Se você vir "Propriedade obrigatória 'Url' ausente", preencha este campo primeiro
- 🔄 Para produção, substitua `localhost:5000` pelo seu domínio real

### Passo 2: Método HTTP

**Campo: Método**
```
POST
```

**Por que POST?**
- Estamos enviando dados (texto do chamado)
- O endpoint `/api/create-ticket-from-text` espera POST

### Passo 3: Cabeçalhos e Corpo

**Clique em "Editar" na seção "Cabeçalhos e corpo"**

#### Cabeçalhos:
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

#### Corpo:
```json
{
  "text": "Meu computador não está funcionando"
}
```

**💡 Dica:** Você pode usar variáveis do Power Fx no corpo:
```json
{
  "text": "{Topic.UserMessage}"
}
```

### Passo 4: Tipo de Dados de Resposta

**Campo: Tipo de dados de resposta**
```
JSON
```

### Passo 5: Salvar Resposta Como

**Campo: Salvar resposta como**
```
Topic.TicketResponse
```

**Esta variável conterá:**
- `Topic.TicketResponse.success` - Se o ticket foi criado
- `Topic.TicketResponse.ticket_id` - ID do ticket criado
- `Topic.TicketResponse.categoria` - Categoria identificada
- `Topic.TicketResponse.prioridade` - Prioridade do ticket

### Passo 6: Configurações Avançadas

#### Tempo Limite (Timeout):
```
30000
```
(30 segundos em milissegundos)

#### Tratamento de Erros:
- ✅ Marque "Gerar um erro" para capturar falhas HTTP

## 📝 YAML Completo Resultante

```yaml
kind: AdaptiveDialog
modelDescription: ação trata de solicitações de chamados, informações e métricas.
beginDialog:
  kind: OnRecognizedIntent
  id: main
  intent:
    displayName: Solicitação de Tickets
    triggerQueries:
      - get tickets
      - buy tickets
      - purchase tickets
      - ticket availability
      - how do I get tickets?
      - can I buy a ticket?
      - reserve a ticket
      - book tickets
      - order tickets online
      - where can I get tickets?
      - preciso abrir um chamado
      - meu computador não funciona
      - problema técnico
      - suporte

  actions:
    - kind: HttpRequestAction
      id: createTicketRequest
      url: "http://localhost:5000/api/create-ticket-from-text"
      method: POST
      headers:
        Content-Type: "application/json"
        Accept: "application/json"
      body: |
        {
          "text": "{Topic.UserMessage}"
        }
      timeout: 30000
      responseDataType: JSON
      saveResponseAs: Topic.TicketResponse
      
    - kind: SendActivity
      id: sendTicketResponse
      activity:
        text: |
          {if(Topic.TicketResponse.success, 
            Concatenate(
              "✅ Chamado criado com sucesso!\n",
              "🎫 ID: ", Topic.TicketResponse.ticket_id, "\n",
              "📂 Categoria: ", Topic.TicketResponse.categoria, "\n",
              "⚡ Prioridade: ", Topic.TicketResponse.prioridade
            ),
            Concatenate(
              "❌ Erro ao criar chamado: ", 
              Topic.TicketResponse.error
            )
          )}

inputType: {}
outputType: {}
```

## 🧪 Teste da Configuração

### Teste 1: Verificação Básica
1. **Salve** a configuração
2. **Teste** o tópico com: "Meu computador não liga"
3. **Verifique** se a resposta contém o ID do ticket

### Teste 2: Diferentes Tipos de Problema
```
Exemplos de teste:
- "Não consigo acessar a internet"
- "Preciso instalar um software"
- "Minha impressora não funciona"
- "Esqueci minha senha"
```

### Teste 3: Verificação de Erros
- Teste com texto vazio
- Teste com API desligada
- Verifique se as mensagens de erro aparecem

## 🔍 Troubleshooting

### Erro: "Propriedade obrigatória 'Url' ausente"
**Solução:** Preencha o campo URL primeiro

### Erro: "Connection refused"
**Solução:** 
1. Verifique se a API está rodando: `python app.py`
2. Teste manualmente: `python test_api_endpoints.py`

### Erro: "Timeout"
**Solução:**
1. Aumente o timeout para 60000ms
2. Verifique a performance da API

### Resposta vazia ou inválida
**Solução:**
1. Verifique os cabeçalhos Content-Type
2. Confirme o formato JSON do corpo
3. Teste o endpoint manualmente

## 📊 Monitoramento

### Variáveis para Debug:
```
Topic.TicketResponse.trace_id - Para rastreamento
Topic.TicketResponse.confianca - Confiança da classificação
```

### Logs Úteis:
- Status HTTP da resposta
- Tempo de resposta
- Conteúdo da resposta JSON

## 🚀 Próximos Passos

1. ✅ **Teste básico funcionando**
2. 🔄 **Configurar para produção** (trocar localhost)
3. 🎨 **Melhorar mensagens de resposta**
4. 📈 **Adicionar métricas e logs**
5. 🔐 **Implementar autenticação** (se necessário)

## 💡 Dicas Importantes

- **Sempre teste localmente primeiro** antes de configurar no Copilot
- **Use o script de teste** para validar a API
- **Monitore os logs** da aplicação Flask durante os testes
- **Documente as variáveis** Power Fx que você criar
- **Teste cenários de erro** para garantir robustez