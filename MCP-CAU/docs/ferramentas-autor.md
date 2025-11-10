# Ferramentas de autoria e validação

Guia prático para construir, editar e validar tópicos do Microsoft Copilot Studio em YAML, com ferramentas de autoria, validação, ALM e referências oficiais.

## Objetivo
- Padronizar o conjunto de ferramentas para criar tópicos com segurança, validar YAML e operar exportação/importação via soluções.

## Ferramentas de autoria
- Copilot Studio (web): canvas de autoria e editor de código para visualizar/ajustar YAML quando necessário.
- Extensão Copilot Studio para VS Code (preview):
  - Clona agentes para editar componentes (tópicos, fontes de conhecimento, ações/flows, entidades) com YAML e IntelliSense.
  - Sincroniza alterações diretamente com o ambiente do Copilot Studio.
  - Disponível em Windows/x64 no momento.
  - Referência: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-edit-with-copilot-studio-extension

## Validação e lint
- Topic checker (Copilot Studio): identifica erros e avisos; corrija antes de publicar.
- Validadores YAML:
  - YAML 1.2.2 (especificação): https://yaml.org/spec/1.2.2/
  - YAML Lint (online): https://www.yamllint.com/
- Boas práticas do editor de código:
  - Preferir ajustes no canvas; use o YAML para pequenas correções e clonagem de nós/IDs.
  - Fazer cópia do tópico antes de editar; erros de sintaxe podem quebrar a conversa.
  - Referência: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor

## Nós generativos e fontes de conhecimento
- Nó de respostas generativas: responde com base em fontes definidas no nível do tópico.
- Precedência: fontes no tópico têm prioridade; fontes no agente atuam como fallback.
- Fontes comuns: dados públicos (sites), Bing Web Search, Bing Custom Search e arquivos carregados; alguns conectores exigem autenticação.
- Upload de arquivos suportados (exemplos): PDF, Word, Excel, PowerPoint, TXT, HTML, CSV, XML, JSON, YAML, OpenDocument, EPUB, RTF, Apple iWork, LaTeX.
- Evite editar YAML sem validação; prefira ajustes pelo UI quando possível.
- Referências:
  - Code editor guidance: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
  - Conversational boosting: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/conversational-boosting

## Tópicos de sistema
- Incorporados, adicionados automaticamente e não podem ser excluídos (podem ser desativados).
- Principais: Escalate, End of Conversation, Fallback, Multiple Topics Matched, On Error, Reset Conversation, Sign in.
- Referência: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-system-topics

## Gatilhos (beginDialog.kind)
- Suportados: `OnRecognizedIntent`, `OnUnknownIntent`, `OnEventActivity`.
- Referência: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers

## ALM: soluções e coleções de componentes
- Use soluções (unmanaged) para exportar/importar agentes e componentes entre ambientes.
- Component collections (preview): reutilize tópicos, conhecimento, ações e entidades entre agentes; mova entre ambientes via soluções.
- Restrições:
  - Comentários de tópicos/nós não são exportados.
  - Evite editar componentes diretamente dentro da solução; faça mudanças no Copilot Studio (UI de autoria).
- Diagnóstico de import: baixe o log XML para verificar componentes requeridos e erros.
- Referências:
  - Export/import via soluções: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export
  - Component collections: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-copilot-components

## Fluxo recomendado (passo a passo)
1. Criar/usar uma solução personalizada no ambiente (evite a solução padrão para ALM).
2. Conectar o agente e adicionar coleções de componentes necessárias à solução.
3. Clonar o agente com a extensão do VS Code e editar tópicos/arquivos YAML com IntelliSense.
4. Validar com Topic checker, ajustar gatilhos e verificar variáveis/indentação.
5. Publicar o agente; testar tópicos de sistema e tópicos personalizados.
6. Exportar a solução (unmanaged) para mover entre ambientes; revisar logs de import se necessário.

## Nomenclatura e IDs (atenção)
- Evite pontos no nome de tópicos (`.`): podem impedir exportações corretas em soluções.
- Garanta IDs únicos ao clonar nós e ajustar componentes.
- Referência: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export

## Referências (consolidadas)
- Create and edit topics: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics
- Use the code editor in topics: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor
- Set topic triggers: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-triggers
- Use system topics: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-system-topics
- Export and import agents using solutions: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export
- Create reusable component collections (preview): https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-copilot-components
- Conversational boosting: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/conversational-boosting
- Extensão VS Code (preview): https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-edit-with-copilot-studio-extension

Ferramentas que facilitam criação/edição de tópicos e manutenção de YAML.

## Extensão do Copilot Studio para VS Code (preview)
- Oferece suporte de linguagem, IntelliSense e dicas ao editar componentes do agente (tópicos, actions, knowledge, triggers).
- Após instalar, faça login no Copilot Studio e clone o agente; os componentes são editáveis como arquivos.
- O VS Code já suporta YAML nativamente; a extensão dá assistência adicional.

Fonte: Edit agents in Visual Studio Code (preview) – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-edit-with-copilot-studio-extension

## Editor de código no Copilot Studio
- Mostra a configuração completa do tópico em YAML.
- Útil para copiar nós entre tópicos, atualizar IDs, revisar variáveis.
- Requer atenção: erros de pontuação/sintaxe podem quebrar a conversa; faça cópias antes de editar.

Fonte: Use the code editor in topics – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topics-code-editor

## Power Platform CLI e soluções
- Exportar/empacotar soluções facilita versionamento e controle de origem.
- Fluxo típico: exportar solução, desempacotar, revisar YAML/localmente, importar solução atualizada.

Fonte (visão geral): Dev Blog – Power Platform: https://devblogs.microsoft.com/powerplatform/bells-whistles-building-with-microsoft-copilot-studio/

## Repositórios e exemplos
- Copilot Studio Samples (GitHub): https://github.com/microsoft/CopilotStudioSamples
- Comunidade (discussão sobre YAML e amostras): https://community.powerplatform.com/forums/thread/details/?threadid=921321f7-147e-412d-8701-1e06ffbc23c1

## Validadores
- Especificação YAML 1.2.2: https://yaml.org/spec/1.2.2/
- Validador YAML (exemplo): https://www.yamllint.com/

## Dicas finais
- Mantenha IDs únicos e escopos de variáveis claros (`Topic.`, `Global.`, `System.`).
- Use lint/validação antes de importar no Copilot Studio.
- Integre com controle de versão (Git) para rastrear mudanças em snippets YAML.