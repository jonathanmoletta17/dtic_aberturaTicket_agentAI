# Visão Geral

Este pacote define a base de conhecimento para construir um agente de IA que abra tickets no GLPI a partir de linguagem natural. Objetivo:
- Classificar a categoria correta do serviço.
- Extrair campos mínimos (título, descrição) e específicos por formulário.
- Enviar ao backend um payload canônico para criação do ticket.

Referências:
- Catálogo de categorias (ITILCategory) via API do GLPI.
- Formcreator (formularios por serviço) — será mapeado incrementalmente.

Fluxo de alto nível:
1) Usuário descreve o problema em linguagem natural.
2) Agente classifica a categoria e infere campos (slot‑filling).
3) Agente apresenta resumo e pede confirmação.
4) Backend cria o ticket no GLPI e retorna `ticket_id`.

Separação: toda a documentação e scripts estão em MCP-CAU, isolados do dashboard DTIC.