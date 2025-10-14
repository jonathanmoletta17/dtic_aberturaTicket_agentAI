# Formulários e Esquema Canônico

Este documento define o esquema canônico dos formulários do GLPI (Plugin FormCreator) e consolida o mapeamento a partir de duas fontes de dados:

- Dump SQL: `MCP-CAU/dumps/glpibkp0210.sql` (extração estática)
- API GLPI: usando `API_URL`, `APP_TOKEN` e `USER_TOKEN` em `MCP-CAU/.env` (extração dinâmica)

Os artefatos gerados estão em `MCP-CAU/output/` e servem como base de documentação e conhecimento para a construção do projeto.

## Fontes de Dados

- SQL (dump):
  - Script: `MCP-CAU/scripts/extract_form_fields_from_sql_dump.py`
  - Saída: `MCP-CAU/output/forms_db/<ID>_<SLUG>.json`
  - Exemplo: `MCP-CAU/output/forms_db/1_EMAIL_E_APLICATIVOS_OFFICE_365.json`

- API GLPI:
  - Listagem de formulários: `MCP-CAU/scripts/fetch_formcreator_forms.py` → `MCP-CAU/output/formcreator_forms.json`
  - Categorias ITIL: `MCP-CAU/scripts/fetch_categories.py` → `MCP-CAU/output/itil_categories.json`

## Esquema Canônico

O esquema canônico padroniza a estrutura para trabalho dos agentes e documentação, independente da origem (SQL ou API):

```json
{
  "form": {
    "id": number,
    "name": string,
    "is_active": number, // 1 ativo, 0 inativo
    "slug": string
  },
  "sections": [
    {
      "id": number,
      "name": string,
      "order": number,
      "questions": [
        {
          "id": number,
          "name": string,
          "fieldtype": string, // ex.: select, text, checkbox
          "required": number, // 1 obrigatório, 0 opcional
          "default_values": string|null,
          "section_id": number,
          "order": number|null
        }
      ]
    }
  ],
  "questions": [ // index plano (opcional)
    {
      "id": number,
      "name": string,
      "fieldtype": string,
      "required": number,
      "default_values": string|null,
      "section_id": number,
      "order": number|null
    }
  ]
}
```

## Mapeamento para GLPI (FormCreator)

- Tabela `glpi_plugin_formcreator_forms` → nó `form`
- Tabela `glpi_plugin_formcreator_sections` → array `sections`
- Tabela `glpi_plugin_formcreator_questions` → array `sections[].questions` e índice `questions`

Observações:
- O dump SQL atual contém `INSERT ... VALUES` em blocos; o parser identifica grupos de valores e reconstrói o relacionamento por `section_id`.
- Em alguns ambientes, `INSERT ... SELECT` ou `multi-line VALUES` exigem ajustes no parser. Hoje cobrimos `VALUES(...)` simples.

## Exemplo (do dump SQL)

Arquivo: `MCP-CAU/output/forms_db/1_EMAIL_E_APLICATIVOS_OFFICE_365.json`

```json
{
  "form": {
    "id": 1,
    "name": "EMAIL E APLICATIVOS OFFICE 365",
    "is_active": 1,
    "slug": "EMAIL_E_APLICATIVOS_OFFICE_365"
  },
  "sections": [
    {
      "id": 1,
      "name": "Dados Gerais",
      "order": 1,
      "questions": [
        {
          "id": 1,
          "name": "Este atendimento é para quem?",
          "fieldtype": "select",
          "required": 0,
          "default_values": null,
          "section_id": 1,
          "order": null
        }
      ]
    }
  ],
  "questions": [
    {
      "id": 1,
      "name": "Este atendimento é para quem?",
      "fieldtype": "select",
      "required": 0,
      "default_values": null,
      "section_id": 1,
      "order": null
    }
  ]
}
```

## Lista de Formulários (API GLPI)

Arquivo: `MCP-CAU/output/formcreator_forms.json`

Resumo:
- Total: 11 formulários
- Ativos (is_active=1): 8
- Inativos (is_active=0): 2

Principais nomes:
- `EMAIL E APLICATIVOS OFFICE 365` (id=1)
- `NOMEIA / EXONERA` (id=2)
- `PROA-ACESSO` (id=4)
- `REQUISIÇÃO` (id=5)
- `IMPRESSORA` (id=6)
- `REDE` (id=7)
- `SISTEMAS INTERNOS` (id=8)
- `INCIDENTE` (id=9)
- `INFRAESTRUTURA` (id=10, inativo)
- `Tranferência de Equipamentos` (id=11, inativo)

## Categorias ITIL (API GLPI)

Arquivo: `MCP-CAU/output/itil_categories.json`

Campos relevantes:
- `id`, `name`, `completename`, `entities_id`, `comment`, `itil_categories_id`

Exemplos:
- `EMAIL` → `ACESSO A SISTEMAS > OFFICE 365 > EMAIL`
- `NOVO USUÁRIO` → `ACESSO A SISTEMAS > OFFICE 365 > EMAIL > NOVO USUÁRIO`
- `IMPRESSORA` → `DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA`
- `REDE` → `ACESSO A SISTEMAS > REDE`
- `OFFICE 365` → `ACESSO A SISTEMAS > OFFICE 365`

Para a lista completa, consultar o JSON.

## Geração e Reprodutibilidade

1) Extrair do dump SQL:
```
python MCP-CAU/scripts/extract_form_fields_from_sql_dump.py "MCP-CAU/dumps/glpibkp0210.sql"
```

2) Atualizar READMEs dos formulários com campos extraídos:
```
python MCP-CAU/scripts/update_form_docs_from_db.py
```

3) Consultar API GLPI (FormCreator e Categorias):
```
python MCP-CAU/scripts/fetch_formcreator_forms.py
python MCP-CAU/scripts/fetch_categories.py
```

Pré-requisitos:
- `MCP-CAU/.env` com `API_URL`, `APP_TOKEN`, `USER_TOKEN` válidos.

## Limitações e Próximos Passos

- Dump atual produz 1 formulário com 1 seção e 1 questão; ao ampliar o parser, poderemos cobrir mais variações de `INSERT` e obter todos os itens.
- Detalhes avançados de perguntas (valores de escolha, validações, visibilidades condicionais) podem exigir consulta adicional de tabelas relacionadas ou da API.
- Próximo: enriquecer cada formulário em `MCP-CAU/forms/<FORM>/README.md` com:
  - Campos detalhados, exemplos de preenchimento e regras de negócio
  - Categoria ITIL esperada e roteamento padrão
  - Integração no pipeline do agente (docs/30_PIPELINE_AGENTE.md)


## Esquema Canônico de Ticket
```json
{
  "category_slug": "EMAIL_APPS_365",
  "itilcategories_id": 20,
  "title": "Problema no Outlook para enviar e-mails",
  "description": "Desde ontem não consigo enviar...",
  "location": "xxxx",
  "contact_phone": "xxxx",
  "service_type": "CRIACAO_LISTA",
  "requester_identifier": "email@empresa.com",
  "users_id_requester": null,
  "attachments": []
}
```

### Mapeamento para GLPI `POST /Ticket`
- `name` ← `title`
- `content` ← `description`
- `itilcategories_id` ← resolvido pelo catálogo
- `requesttypes_id` ← política (ex.: 1)
- `entities_id` ← entidade ativa
- `urgency`/`priority` ← opcional por política

## Modelos de Formulário por Categoria

### EMAIL_APPS_365
Campos mínimos:
- `location` (string, obrigatório)
- `contact_phone` (string, obrigatório)
- `service_type` (enum, obrigatório): CRIACAO_LISTA, REMOVER_LISTA, CAIXA_COMPARTILHADA, GRUPOS_365, OUTLOOK_PROBLEMA, TEAMS_PROBLEMA, ONEDRIVE_PROBLEMA
- `description` (text, obrigatório)

### IMPRESSORA
- `equipment_model` (string)
- `asset_tag` (string)
- `location` (string, obrigatório)
- `description` (text, obrigatório)

### REDE
- `operation` (enum, obrigatório): CRIAR_USUARIO, CRIAR_GRUPO, ACESSO_PASTA, RESET_SENHA
- `location` (string)
- `description` (text, obrigatório)

### PROA_ACESSO
- `system_group` (string, obrigatório)
- `user_identifier` (string, obrigatório)
- `description` (text, obrigatório)

### SISTEMAS_INTERNOS
- `system` (enum, obrigatório): AFE, Agenda, FSE, CEC, GDC, LAI, RHE, SOM, SPI, Tunel_PROCERGS, Outro
- `operation` (enum, obrigatório): LIBERAR, REMOVER, DESBLOQUEAR
- `user_identifier` (string, obrigatório)
- `description` (text, obrigatório)

### INCIDENTE
- `impact` (enum): BAIXO, MEDIO, ALTO
- `location` (string)
- `description` (text, obrigatório)

### REQUISICAO
- `service_type` (string, obrigatório)
- `location` (string)
- `description` (text, obrigatório)

## Seed de Schemas
O arquivo `config/form_schemas.json` contém o seed com os campos acima e agora está preenchido com os `itilcategories_id` reais do seu GLPI (vide `docs/10_CATALOGO_CATEGORIAS.md`).

Diretrizes:
- Utilize subcategorias específicas quando aplicável (ex.: `DTIC > INFRAESTRUTURA > PROBLEMA DE REDE` para incidentes de rede).
- Em 365, use `OFFICE 365` (id 20) como categoria genérica; quando necessário, refine para `EMAIL` (id 2) ou ações específicas como `CRIAR EQUIPE SHAREPOINT` (id 36).