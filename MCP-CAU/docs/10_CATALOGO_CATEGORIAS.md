# Catálogo de Categorias (ITILCategory)

Categorias observadas no catálogo de serviços:
- EMAIL_APPS_365 — Email e Aplicativos Office 365.
- IMPRESSORA — Problemas em impressoras.
- INCIDENTE — Problemas gerais (equipamentos/rede/outros).
- PROA_ACESSO — Solicitação de acesso a grupo (PROA).
- REDE — Usuário/Grupo, acesso a pasta, reset de senha.
- REQUISICAO — Pedidos de serviço ao suporte técnico.
- SISTEMAS_INTERNOS — Operações em sistemas internos (AFE, Agenda, FSE etc.).

## Como obter os IDs reais
Use `scripts/fetch_categories.py` para listar categorias do GLPI (ITILCategory). O resultado é salvo em `output/itil_categories.json` com os campos `id`, `name`, `completename`, `entities_id`, `is_helpdesk_visible`.

Após coletar, preencha `config/form_schemas.json` com `itilcategories_id` correspondente a cada `slug`.

## Observações
- As categorias podem ser hierárquicas; use `completename` para diferenciar caminhos.
- Nem todo serviço Formcreator mapeia diretamente 1:1 com uma `ITILCategory`; se houver divergência, documentar a regra de roteamento.

## IDs reais mapeados (coleta em seu GLPI)
- `EMAIL_APPS_365` → `itilcategories_id=20` (`DTIC > ACESSO A SISTEMAS > OFFICE 365`).
- `IMPRESSORA` → `itilcategories_id=14` (`IMPRESSORA`). Subcategorias: `ATOLAMENTO` (57), `TROCA DE TONNER` (71), `MOVIMENTAÇÃO FISICA` (72).
- `REDE` → `itilcategories_id=21` (`ACESSO A SISTEMAS > REDE`). Subcategorias: `LIBERAÇÃO DE ACESSO` (22), `RESET DE SENHA` (24), `WIFI` (37), `TÚNEL PROCERGS` (33), `NOVO USUÁRIO` (35).
- `PROA_ACESSO` → `itilcategories_id=17` (`ACESSO A SISTEMAS > SOE > PROA`). Subcategorias: `ADICIONAR A GRUPO` (31), `REMOVER DE GRUPO` (30).
- `SISTEMAS_INTERNOS` → `itilcategories_id=40` (`DTIC > SISTEMAS`). Subcategorias: `INSTALAÇÃO DE SOFTWARE` (46), `CONFIGURAÇÃO DE SOFTWARE` (47), `ALTERAÇÃO DE ACESSO` (49), `REMOÇÃO DE ACESSO SISTEMA` (48).
- `INCIDENTE` → `itilcategories_id=7` (`AJUDA E SUPORTE`). Para incidentes de rede use especificamente `DTIC > INFRAESTRUTURA > PROBLEMA DE REDE` (51) quando aplicável.
- `REQUISICAO` → `itilcategories_id=28` (`AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI > REQUISIÇÃO`).

Fonte: `MCP-CAU/output/itil_categories.json` gerado via `scripts/fetch_categories.py`.

## Resumo da Coleta Atual

- Fonte: `MCP-CAU/output/itil_categories.json`
- Campos: `id`, `name`, `completename`, `entities_id`, `comment`, `is_helpdesk_visible`, `itil_categories_id`
- Observação: `completename` reflete a hierarquia e é ideal para mapeamento 1:1 com serviços de formulários.

### Amostras da Estrutura

| id | name           | completename                                                |
|----|----------------|-------------------------------------------------------------|
| 20 | OFFICE 365     | ACESSO A SISTEMAS > OFFICE 365                             |
| 2  | EMAIL          | ACESSO A SISTEMAS > OFFICE 365 > EMAIL                     |
| 23 | ALTERAR PLANO  | ACESSO A SISTEMAS > OFFICE 365 > EMAIL > ALTERAR PLANO     |
| 21 | REDE           | ACESSO A SISTEMAS > REDE                                   |
| 33 | TÚNEL PROCERGS | ACESSO A SISTEMAS > REDE > TÚNEL PROCERGS                  |
| 14 | IMPRESSORA     | IMPRESSORA                                                  |
| 15 | IMPRESSORA     | DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA              |

## Como Reexecutar

```
python MCP-CAU/scripts/fetch_categories.py
```

## Diretrizes de Mapeamento

- Usar `completename` para decidir subcategoria final quando o formulário tiver múltiplas variações (ex.: EMAIL: novo usuário, caixa compartilhada, exclusão, etc.).
- Manter o `itilcategories_id` associado ao `slug` do formulário em `config/form_schemas.json`.
- Documentar exceções quando o roteamento não for 1:1.