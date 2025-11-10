# Boas práticas para edição de tópicos em YAML

Recomendações para criar, editar e manter tópicos do Copilot Studio em YAML com qualidade e segurança.

## Princípios gerais
- Prefira editar no canvas e usar o YAML para revisões pontuais, clonagem de nós e ajustes de IDs.
- Faça uma cópia do tópico antes de editar em YAML; erros de sintaxe podem quebrar a conversa e o suporte técnico não cobre correções no editor de código.
- Valide a sintaxe com uma ferramenta de YAML antes de salvar.

Fontes:
- Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor

## Nomenclatura e IDs
- Use nomes sem ponto (`.`) nos tópicos: soluções com agentes que possuem pontos no nome dos tópicos não exportam corretamente.
- Garanta IDs únicos ao clonar nós (`id:`); evite colisões entre `Question`, `ConditionGroup`, `SendMessage` etc.

Fonte: Export and import agents using solutions – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export

## Gestão de tópicos
- Use o Topic checker para identificar erros e avisos; corrija erros antes de publicar.
- Controle `On/Off` para trabalhar em rascunho; publicar não muda o status de On/Off.
- Para encerrar conversas:
  - `End current topic`: encerra tópico atual e retorna ao chamador.
  - `End all topics`: encerra todos os tópicos ativos; combine com `End Conversation` para informar o usuário.
  - Para limpar variáveis globais, use `Clear all variables` antes de `End all topics`.

Fonte: Manage topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-topic-management

## Variáveis e escopo
- `Topic.` para variáveis locais ao tópico; `Global.` para variáveis globais ao agente; `System.` para valores do sistema (ex.: texto da atividade).
- Evite usar `Global.` sem necessidade; dificulta isolamento e testes.

## Integração com Power Automate
- Guarde o `flowId` correto ao usar `InvokeFlowAction`; se o fluxo mudar, atualize o ID.
- Considere editar o ID no YAML quando a sincronização demorar.

Fonte: Dev Blog (Code editor e CLI): https://devblogs.microsoft.com/powerplatform/bells-whistles-building-with-microsoft-copilot-studio/

## Reuso e ALM
- Use “Component collections” (preview) para compartilhar tópicos, conhecimento, ações e entidades entre agentes.
- Exporte/importa coleções via soluções; revise componentes requeridos antes de exportar.

Fonte: Create reusable component collections (preview) – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-copilot-components

## Importação/Exportação e limites
- Exporte agentes via soluções (unmanaged). Comentários em nível de tópico/nó não são exportados.
- Não remova/edite componentes de agente diretamente na solução; faça mudanças no UI padrão de autor.
- Se o import falhar, baixe o log XML e verifique componentes requeridos.

Fonte: Export and import agents using solutions – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export

## Checklist de revisão YAML
- IDs únicos para todos os nós.
- Nomes de tópico sem ponto (`.`).
- Indentação consistente com espaços; sem TABs.
- Variáveis com escopo correto (`Topic.`, `Global.`, `System.`).
- Condições (`= ...`) testadas para ramos `actions` e `elseActions`.
- Validação externa de YAML antes de salvar.

## Ferramentas úteis
- Extensão do Copilot Studio para VS Code (preview): IntelliSense e edição de YAML com login no ambiente.
- Validadores: YAML 1.2.2, YAML Checker.

Fontes:
- Edit agents in Visual Studio Code (preview) – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-edit-with-copilot-studio-extension
- YAML 1.2.2: https://yaml.org/spec/1.2.2/
- YAML Checker: https://www.yamllint.com/