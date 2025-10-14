# Pipeline do Agente LLM

## Etapas
1. Classificação da Categoria
   - Detectar categoria por palavras-chave/sinônimos (ex.: "Outlook", "Teams" → EMAIL_APPS_365; "impressora" → IMPRESSORA; "VPN", "pasta de rede" → REDE; nomes de sistemas → SISTEMAS_INTERNOS).
   - Se confiança baixa, pedir confirmação de categoria.

2. Slot‑filling (extração de campos)
   - Sempre: `title`, `description`.
   - MVP: `location = "xxxx"`, `contact_phone = "xxxx"`.
   - Específicos: inferir `service_type`/`operation` por sinônimos (ex.: "criar caixa compartilhada").

3. Resumo e Confirmação
   - Exibir categoria, título e descrição; permitir correções.

4. Abertura
   - Enviar payload canônico ao backend.
   - Backend resolve `users_id_requester`/`itilcategories_id` e cria ticket.

5. Pós‑abertura
   - Retornar `ticket_id`; oferecer anexos/seguidores.

## Validações
- Título 6–120 caracteres, sem ruído.
- Descrição estruturada (contexto, passos, erro, impacto).
- Campos obrigatórios por categoria: perguntar apenas o que faltar.
- Logs e rastreabilidade das decisões do agente.