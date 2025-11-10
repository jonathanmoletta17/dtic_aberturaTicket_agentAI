# Exemplos completos de tópicos em YAML

Modelos práticos para copiar, adaptar e importar no Copilot Studio.

## 1) Intenção com entidade pré‑construída e condição
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnRecognizedIntent
  id: main
  intent:
    displayName: Shipping charge with state and confirmation
    triggerQueries:
      - Buy items
      - Purchase item
actions:
  - kind: SendMessage
    id: welcome
    message: I am happy to help you place your order.

  - kind: Question
    id: ask-state
    alwaysPrompt: false
    variable: init:Topic.State
    prompt: To what state will you be shipping?
    entity: StatePrebuiltEntity

  - kind: ConditionGroup
    id: west-coast
    conditions:
      - id: is-westcoast
        condition: =Topic.State = "California" || Topic.State = "Washington" || Topic.State = "Oregon"
        elseActions:
          - kind: SendMessage
            id: extra-charge
            message: There will be an additional shipping charge of $27.50.

  - kind: Question
    id: accept-charge
    alwaysPrompt: false
    variable: init:Topic.ShippingRateAccepted
    prompt: Is that acceptable?
    entity: BooleanPrebuiltEntity

  - kind: ConditionGroup
    id: confirm
    conditions:
      - id: accepted
        condition: =Topic.ShippingRateAccepted = true
        elseActions:
          - kind: SendMessage
            id: goodbye
            message: Thank you and please come again.
```
Referência base: Create and edit topics – Microsoft Learn.

## 2) Boosting generativo com busca em fontes públicas
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnUnknownIntent
  id: main
  priority: -1
actions:
  - kind: SearchAndSummarizeContent
    id: search-content
    userInput: =System.Activity.Text
    variable: Topic.Answer
    moderationLevel: Medium
    additionalInstructions: Use concise tone and add a short summary.
    publicDataSource:
      sites:
        - "example.com/knowledge"
        - "docs.example.org/"

  - kind: ConditionGroup
    id: has-answer
    conditions:
      - id: answer
        condition: =!IsBlank(Topic.Answer)
        actions:
          - kind: SendMessage
            id: return
            message: =Topic.Answer
          - kind: EndDialog
            id: end
            clearTopicQueue: true
```
Referência base: Use the code editor in topics – Microsoft Learn.

Notas de uso de nós generativos:
- Definições de fontes de conhecimento no nível do tópico têm precedência sobre as fontes definidas no nível do agente; o agente usa suas fontes apenas como fallback.
- Fontes comuns incluem dados públicos (por exemplo, sites), Bing Web Search, Bing Custom Search e arquivos carregados; alguns conectores exigem autenticação.
- É possível carregar arquivos (por exemplo: PDF, Word, Excel, PowerPoint, TXT, HTML, CSV, XML, JSON, YAML, OpenDocument, EPUB, RTF, Apple iWork, LaTeX) para priorizar respostas; verifique suporte e limites na documentação oficial.
- Evite editar manualmente YAML sem validação: erros de sintaxe podem quebrar o tópico; prefira ajustes pela interface do Copilot Studio.

Referências:
- Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
- Set topic triggers – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers
- Conversational boosting (orientações) – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/conversational-boosting

## 3) Evento com resposta e integração a fluxo (placeholder)
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnEventActivity
  id: main
  priority: 200
  eventName: app.customer.checkEligibility
actions:
  - kind: SendActivity
    id: notify
    activity: Checking eligibility, one moment please.

  - kind: InvokeFlowAction
    id: check-eligibility
    input:
      binding:
        customerId: =System.Activity.Text
    output:
      binding:
        isEligible: Topic.IsEligible
    flowId: 00000000-0000-0000-0000-000000000000  # substitua pelo GUID real

  - kind: ConditionGroup
    id: result
    conditions:
      - id: eligible
        condition: =Topic.IsEligible = true
        actions:
          - kind: SendMessage
            id: ok
            message: Customer is eligible.
        elseActions:
          - kind: SendMessage
            id: not-ok
            message: Customer is not eligible.
```
Referência (padrões): 365lyf blog para eventos; Dev Blog para fluxo/CLI.

## Observações
- Substitua URLs, entidades e `flowId` por valores do seu ambiente.
- Garanta IDs únicos e validação YAML antes de importar.

Fontes:
- Create and edit topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics
- Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
- 365lyf blog (exemplos de evento): https://365lyf.com/enhancing-copilot-conversations-in-model-driven-power-apps-using-copilot-studio/
- Power Platform Dev Blog: https://devblogs.microsoft.com/powerplatform/bells-whistles-building-with-microsoft-copilot-studio/