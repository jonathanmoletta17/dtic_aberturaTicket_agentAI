# Base de Conhecimento (KB) – Copilot Studio / MCP-CAU

Esta KB registra problemas recorrentes de implementação, suas causas e correções, sempre com referências à documentação oficial do Microsoft Copilot Studio e ao contexto do nosso agente.

## Como usar
- Cada tópico de problema tem: descrição, sintomas, reprodução, causa raiz, correção, referências.
- Os arquivos ficam em `docs/kb/`. Para novos casos, crie um `*.md` seguindo a estrutura padrão.
- Priorize registrar: erros de conteúdo YAML, problemas de autenticação, falhas de validação de payload, inconsistências de tipos e formatação.

## Estrutura sugerida
- Problema
- Sintomas/Logs
- Reproduzir
- Causa raiz
- Correção (passo a passo)
- Impacto/Notas
- Referências oficiais

## Ferramentas de apoio
- Consulte `docs/kb/copilot-yaml-sanitizacao.md` para checklist de sanitização de YAML.
- Use o script `AberturaChamadoAI/scripts/lint_yaml_copilot.py` para detectar tabs, NBSP, CRLF, espaços à direita e inconsistências comuns.