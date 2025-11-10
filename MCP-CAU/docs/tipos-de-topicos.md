# Tipos de tópicos no Microsoft Copilot Studio

Este guia descreve os tipos de tópicos disponíveis no Copilot Studio, seus gatilhos e diferenças de uso ao editar em YAML, com exemplos práticos e referências.

## Visão geral de tópicos
- Tópicos são caminhos de conversa que definem competências do agente.
- Podem ser criados do zero, com auxílio de IA (Copilot), ou a partir de conteúdo.
- A configuração é exibida e pode ser editada no editor de código em YAML.

Fontes:
- Topics in Copilot Studio – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-overview
- Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor

## Categorias principais
- Custom topics (tópicos personalizados): criados pelo autor, podem ter frases de gatilho e composição livre de nós.
- System topics (tópicos de sistema): pré-definidos, tratam eventos comuns (início, fim, fallback, erro, etc.). Não podem ser excluídos; podem ser desativados.
- Generative topics (tópicos com nós generativos): usam nós como `SearchAndSummarizeContent` e “Conversational boosting” quando não há correspondência com outros tópicos.

Fonte: Topics in Copilot Studio.

## Tópicos de sistema (principais)
| Tópico (System topic) | Descrição (resumo) |
| --- | --- |
| Conversation Start | Inicia a conversa (saudação). Pode disparar automaticamente dependendo do cliente. |
| End of Conversation | Encaminha para encerramento e pesquisa de satisfação; marca sessão como resolvida quando apropriado. |
| Escalate | Handoff para um humano (ex.: Omnichannel). Pode ser disparado por frases como “talk to agent” ou por eventos de escalonamento. |
| Fallback | Dispara quando a consulta não corresponde a nenhum tópico com confiança suficiente. |
| Multiple Topics Matched | Quando várias correspondências existem; pergunta ao usuário “o que você quis dizer?”. |
| On Error | Informa ao usuário que ocorreu um erro de usuário; inclui código, ID da conversa e timestamp. |
| Reset Conversation | Reseta a conversa (limpa variáveis e usa conteúdo publicado mais recente). |
| Sign in | Solicita autenticação quando habilitada, no início ou quando um nó exige variáveis autenticadas. |

Fonte: Use system topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-system-topics

## Gatilhos (beginDialog.kind)
- `OnRecognizedIntent`: ativa por frases de gatilho/intenções do tópico.
- `OnUnknownIntent`: usado para boosting/conteúdo generativo quando não há correspondência.
- `OnEventActivity`: dispara em eventos específicos (ex.: integração com apps).

Fonte: Set topic triggers – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers

## Exemplo – Custom topic com intenção reconhecida
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnRecognizedIntent
  id: main
  intent:
    displayName: Lesson 3 - A topic with a condition, variables and a prebuilt entity
    triggerQueries:
      - Buy items
      - Buy online
      - Buy product
      - Purchase item
      - Order product
actions:
  - kind: SendMessage
    id: Sjghab
    message: I am happy to help you place your order.

  - kind: Question
    id: eRH3BJ
    alwaysPrompt: false
    variable: init:Topic.State
    prompt: To what state will you be shipping?
    entity: StatePrebuiltEntity

  - kind: ConditionGroup
    id: sEzulE
    conditions:
      - id: pbR5LO
        condition: =Topic.State = "California" || Topic.State = "Washington" || Topic.State = "Oregon"
        elseActions:
          - kind: SendMessage
            id: X7BFUC
            message: There will be an additional shipping charge of $27.50.
```
Fonte: Create and edit topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics

## Exemplo – Tópico com respostas generativas
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
    additionalInstructions: Include emojis to make responses more fun.
    publicDataSource:
      sites:
        - "www.chessusa.com/"
        - "www.chess.com/"
        - "www.lichess.org/"
    sharePointSearchDataSource: {}

  - kind: ConditionGroup
    id: has-answer-conditions
    conditions:
      - id: has-answer
        condition: =!IsBlank(Topic.Answer)
        actions:
          - kind: EndDialog
            id: end-topic
            clearTopicQueue: true
```
Fonte: Use the code editor in topics – Microsoft Learn.

## Exemplo – Tópico por evento
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnEventActivity
  id: main
  priority: 200
  eventName: Microsoft.PowerApps.Copilot.RequestSparks
actions:
  - kind: SendActivity
    id: notify
    activity: Analyzing request sparks event.
```
Referência (exemplos avançados): 365lyf blog: https://365lyf.com/enhancing-copilot-conversations-in-model-driven-power-apps-using-copilot-studio/