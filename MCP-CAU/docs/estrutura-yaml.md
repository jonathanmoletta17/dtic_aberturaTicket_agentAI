# Estrutura YAML de tópicos no Microsoft Copilot Studio

Este guia explica como estruturar e editar tópicos de agentes no Microsoft Copilot Studio usando YAML, com foco em chaves, nós comuns, variáveis, entidades e gatilhos. Inclui exemplos práticos e links diretos para documentação oficial e conteúdos técnicos.

## Visão geral
- Tópicos podem ser escritos e editados em um editor de código que exibe a configuração em YAML.
- O YAML é gerado automaticamente a partir do canvas de autoria, mas pode ser revisado manualmente quando necessário.
- O formato é legível e usa indentação para representar estruturas (listas, dicionários, valores).

Fontes:
- Create and edit topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics
- Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
- Power Platform Dev Blog (YAML nos bastidores): https://devblogs.microsoft.com/powerplatform/bells-whistles-building-with-microsoft-copilot-studio/
- Set topic triggers – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers

## Estrutura de alto nível
- `kind`: tipo do diálogo (normalmente `AdaptiveDialog`).
- `beginDialog`: define o gatilho inicial do tópico (ex.: `OnRecognizedIntent`, `OnUnknownIntent`, `OnEventActivity`).
- `id` e `priority`: identificadores e prioridade de execução do gatilho.
- `actions`: sequência de nós (passos da conversa) executados quando o tópico é disparado.

Exemplo simplificado (gatilho por intenção reconhecida):

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

  - kind: Question
    id: 6lyBi8
    alwaysPrompt: false
    variable: init:Topic.ShippingRateAccepted
    prompt: Is that acceptable?
    entity: BooleanPrebuiltEntity

  - kind: ConditionGroup
    id: 9BR57P
    conditions:
      - id: BW47C4
        condition: =Topic.ShippingRateAccepted = true
        elseActions:
          - kind: SendMessage
            id: LMwySU
            message: Thank you and please come again.
```

Referência: trecho baseado no artigo “Create and edit topics”.

## Gatilhos (`beginDialog.kind`)
- `OnRecognizedIntent`: dispara por correspondência de frases de gatilho (intenção) definidas no tópico.
- `OnUnknownIntent`: útil para tópicos de “conversational boosting”/respostas generativas quando não há correspondência com outros tópicos.
- `OnEventActivity`: dispara em eventos específicos enviados ao agente (ex.: integrações ou eventos do cliente). 
- `OnMessageReceived`: dispara a cada mensagem do usuário, quando configurado.
- `OnDtmfKeyPress`: usado em experiências de voz para captar teclas DTMF.

Exemplo (gatilho desconhecido com respostas generativas):
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

Referência: “Use the code editor in topics”.

## Nós comuns em `actions`
- `SendMessage`/`SendActivity`: envia mensagem simples ou mensagem rica (inclui `activity:` em experiências de voz/cartões).
- `Question`: pergunta ao usuário; pode vincular variável e entidade de extração.
- `ConditionGroup`: agrupa condições com `condition`, `actions` e `elseActions`.
- `EndDialog`: encerra o diálogo atual; com `clearTopicQueue: true` encerra todos os tópicos ativos.
- `InvokeFlowAction`: chama um fluxo do Power Automate.
- `SetVariable`/`ParseValue`: manipula variáveis e converte estruturas.
- `SearchAndSummarizeContent`: nó generativo para buscar e sumarizar fontes de conhecimento.

Exemplo (voz com `SendActivity`, `SetVariable`, `ConditionGroup`):
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnDtmfKeyPress
  id: main
  dtmfKey: Num9
actions:
  - kind: ConditionGroup
    id: conditionGroup_Im7G18
    conditions:
      - id: conditionItem_a2ax5d
        condition: =!IsEmpty(Global.GenAnsVoiceRef)
        actions:
          - kind: SetVariable
            id: setVariable_dgK3w7
            variable: Topic.NumReferences
            value: =CountRows(Global.GenAnsVoiceRef)
          - kind: ConditionGroup
            id: conditionGroup_YRrOBv
            conditions:
              - id: conditionItem_hD1dXt
                condition: =Topic.NumReferences = 1
                actions:
                  - kind: SendActivity
                    id: sendActivity_42mrfG
                    activity:
                      speak:
                        - The following reference was consulted.
```

Referência: “Use generative answers in your voice-enabled agents”.

## Variáveis e escopos
- `Topic.`: variáveis locais ao tópico (ex.: `Topic.State`, `Topic.Answer`).
- `Global.`: variáveis globais ao agente (ex.: `Global.GenAnsVoiceRef`).
- `System.`: valores do sistema (ex.: `System.Activity.Text`).

Boas práticas:
- Garanta IDs únicos ao clonar nós pelo YAML.
- Use escopos adequados (`Topic.` vs `Global.`) para evitar colisões e facilitar testes.

## Entidades
- `Prebuilt` (ex.: `StatePrebuiltEntity`, `BooleanPrebuiltEntity`) usadas em perguntas para reconhecer valores.
- Entidades personalizadas também podem ser mapeadas via canvas (o YAML refletirá esse mapeamento).

## Sintaxe e validação
- Extensão de arquivos: `.yaml` ou `.yml`.
- Indentação por espaços (atenção à consistência, não use TABs).
- Suporte a strings, números, booleanos, listas e dicionários.
- Valide a sintaxe com validadores de YAML quando editar manualmente.

Fontes de referência:
- Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
- Create and edit topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics
- Use generative answers in voice – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/voice-generative-answers