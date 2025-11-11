# Tópico "autenticar usuário" – `authResponse` tipo inválido

## Problema
Erros ao usar `authResponse` com `responseSchema: Any` e/ou `variables` com `type: any` no tópico de autenticação.

## Sintomas/Logs
- Mensagem de erro genérica de conteúdo/validação no Copilot Studio.
- Falha de publicação ou execução do tópico com referência a tipo inválido.

## Reproduzir
1. Configurar `HttpRequestAction` com `response: Topic.authResponse` e `responseSchema: Any`.
2. Definir em `outputType` `authResponse` com `type: Any`.
3. Definir em `variables` `Topic.authResponse` com `type: any`.
4. Publicar/rodar e observar erro.

## Causa raiz
- Inconsistência de tipos entre `responseSchema`, `outputType` e `variables`.
- O parser do Copilot Studio pode rejeitar `any` minúsculo e/ou exigir tipos mais específicos para payloads JSON.

## Correção
- Padronizar o tipo do `authResponse` como `Object` em `responseSchema`, `outputType` e `variables`.
- Padronizar tipos das demais `variables` para `String` (maiúsculo) quando forem textos.

### Exemplo de ajuste
```
# Antes
responseSchema: Any

outputType:
  properties:
    authResponse:
      type: Any

variables:
  - name: Topic.authResponse
    type: any

# Depois
responseSchema: Object

outputType:
  properties:
    authResponse:
      type: Object

variables:
  - name: Topic.authResponse
    type: Object
  - name: Topic.login
    type: String
  # ... demais variáveis String em maiúsculo
```

## Impacto/Notas
- `Object` representa melhor a resposta JSON do backend.
- Evita erros de conteúdo/validação do parser.

## Referências
- Solucionar erros no Copilot Studio Kit: https://learn.microsoft.com/pt-br/microsoft-copilot-studio/guidance/kit-troubleshoot
- Configurar autenticação do usuário: https://learn.microsoft.com/pt-br/microsoft-copilot-studio/configuration-end-user-authentication
- Compreender códigos de erro: https://learn.microsoft.com/pt-br/microsoft-copilot-studio/error-codes