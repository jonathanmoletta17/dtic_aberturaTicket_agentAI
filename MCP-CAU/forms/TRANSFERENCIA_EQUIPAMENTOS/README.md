# TRANSFERENCIA_EQUIPAMENTOS

- Formulário: `Tranferência de Equipamentos`
- GLPI Form ID: `11`
- Ativo: `0`
- Descrição: `Transferencia de Equipamentos`
- Uso (count): `0`
- Fonte (JSON): `../../output/forms/11_TRANSFERENCIA_EQUIPAMENTOS.json`

## Visão Geral

- Finalidade: transferir equipamentos entre unidades/usuários.
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI` (id ~ 28, ou correlato de movimentação).

## Categoria ITIL alvo

- ID: `28`
- Caminho: `AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI > REQUISIÇÃO`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Dados esperados: patrimônio, origem, destino, justificativa, janela de transferência.

## Regras de Negócio

- Verificar autorização e registro de responsabilidade.
- Atualizar inventário após conclusão.

## Pipeline do Agente

- Coletar dados de patrimônio e unidades, validar autorização, e abrir requisição com categoria adequada.

## Roteamento por Operação

- `DEFAULT` → `AJUDA E SUPORTE > MOVIMENTO DE EQUIPAMENTOS DE TI > REQUISIÇÃO` (ID 28)