# MCP-CAU – Base de Documentação e Mapeamento para Agente de Abertura de Ticket

Este repositório interno organiza toda a documentação, configuração e scripts auxiliares para mapear o catálogo e os formulários do GLPI e preparar um agente de IA capaz de abrir chamados a partir de linguagem natural.

Estrutura:
- `docs/` — visão geral, categorias, formulários, pipeline do agente e validações.
- `config/` — arquivos JSON de schemas e mapeamentos (seed e futuros IDs reais).
- `scripts/` — utilitários para consultar categorias (ITILCategory) no GLPI.
- `output/` — resultados das consultas (ex.: `itil_categories.json`).

Como usar os scripts:
1. Copie `.env.example` para `.env` e preencha `API_URL`, `APP_TOKEN`, `USER_TOKEN`.
2. Instale dependências: `pip install requests python-dotenv`.
3. Execute: `python scripts/fetch_categories.py`.
4. Verifique `output/itil_categories.json` e atualize `config/form_schemas.json` com os IDs.

Observação: Esta pasta é independente do dashboard DTIC; não altera o backend/front existentes.