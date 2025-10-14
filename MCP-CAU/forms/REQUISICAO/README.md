# REQUISICAO

- Formulário: `REQUISIÇÃO`
- GLPI Form ID: `5`
- Ativo: `1`
- Descrição: `Atendimento ao usuário //  Suporte Técnico`
- Uso (count): `1790`
- Fonte (JSON): `../../output/forms/5_REQUISICAO.json`

## Visão Geral

- Finalidade: requisições gerais ao suporte técnico.
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI > REQUISIÇÃO` (id ~ 28).

## Categoria ITIL alvo

- ID: `28`
- Caminho: `AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI > REQUISIÇÃO`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Campos mínimos: descrição clara, unidade, contato, impacto esperado.

## Regras de Negócio

- Validar se é requisição (serviço) ou incidente (falha) para roteamento correto.
- Incluir aprovação quando envolver movimentação de ativos.

## Pipeline do Agente

- Coletar dados básicos, determinar escopo, e abrir requisição com categoria definida.

## Roteamento por Operação

- `DEFAULT` → `AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI > REQUISIÇÃO` (ID 28)