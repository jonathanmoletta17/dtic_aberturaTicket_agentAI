# EMAIL_APPS_365

- Formulário: `EMAIL E APLICATIVOS OFFICE 365`
- GLPI Form ID: `1`
- Ativo: `1`
- Descrição: `Email -Criação\Remoção\Listas|Caixas Compartilhadas| Grupos 365`
- Uso (count): `953`

## Visão Geral

- Finalidade: operações de e-mail e Office 365 (novo usuário, caixa compartilhada, listas, exclusão, alteração de plano/licença).
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` (esquema canônico) e `docs/10_CATALOGO_CATEGORIAS.md` (categorias ITIL).

## Categoria ITIL (roteamento)

- Base: `ACESSO A SISTEMAS > OFFICE 365` (`id ~ 20`).
- Subcategorias comuns (exemplos):
  - `EMAIL` (id ~ 2)
  - `NOVO USUÁRIO` (id ~ 3)
  - `CAIXA COMPARTILHADA` (id ~ 4)
  - `LISTA PUBLICA` (id ~ 5)
  - `EXCLUSÃO` (id ~ 6)
  - `ALTERAR PLANO / LICENÇA` (id ~ 23)
- Referência completa: `MCP-CAU/output/itil_categories.json`.

## Categoria ITIL alvo

- ID: `20`
- Caminho: `ACESSO A SISTEMAS > OFFICE 365`

## Campos do Formulário (dump SQL)

Fonte: `../../output/forms_db/1_EMAIL_E_APLICATIVOS_OFFICE_365.json`

- Seção: Dados Gerais (ordem: 1)
  - Este atendimento é para quem? — tipo: `select`, obrigatório: `0`

## Regras de Negócio

- Identificar o tipo de solicitação (novo usuário, caixa compartilhada, etc.) e mapear para subcategoria ITIL correspondente.
- Validar se o solicitante possui permissão para criar/remover caixas/listas (fluxos internos do Office 365).
- Garantir consistência de dados de usuário (nome, e-mail, unidade) para criar/ajustar licenças.

## Exemplos de Preenchimento

- Novo usuário: nome completo, e-mail desejado, unidade, perfil/licença.
- Caixa compartilhada: nome da caixa, membros, permissões de acesso.
- Alterar plano: usuário alvo, plano atual, plano desejado, justificativa.

## Pipeline do Agente

- Entrada: texto do usuário → classificador identifica operação (e.g., "criar e-mail", "caixa compartilhada").
- Normalização: extrair campos obrigatórios conforme seção "Campos do Formulário".
- Roteamento: selecionar categoria ITIL alvo (ver seção Categoria ITIL).
- Abertura de chamado: criar ticket com campos estruturados e justificativa.

## Roteamento por Operação

- `CRIACAO_LISTA` → Categoria `LISTA PUBLICA` (ID 5)
- `REMOVER_LISTA` → Categoria `LISTA PUBLICA` (ID 5)
- `CAIXA_COMPARTILHADA` → Categoria `CAIXA COMPARTILHADA` (ID 4)
- `GRUPOS_365` → Base `OFFICE 365` (ID 20)
- `OUTLOOK_PROBLEMA` → Categoria `EMAIL` (ID 2)
- `TEAMS_PROBLEMA` → Base `OFFICE 365` (ID 20)
- `ONEDRIVE_PROBLEMA` → Base `OFFICE 365` (ID 20)

## Fontes e IDs

- JSON API (form): `../../output/forms/1_EMAIL_APPS_365.json`
- JSON dump SQL (campos): `../../output/forms_db/1_EMAIL_E_APLICATIVOS_OFFICE_365.json`
- Categorias ITIL: `../../output/itil_categories.json`