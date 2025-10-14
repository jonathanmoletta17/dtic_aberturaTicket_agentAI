# REDE

- Formulário: `REDE`
- GLPI Form ID: `7`
- Ativo: `1`
- Descrição: `Criação de usuário/liberação de acesso a pasta /Reset de Senha`
- Uso (count): `812`
- Fonte (JSON): `../../output/forms/7_REDE.json`

## Visão Geral

- Finalidade: contas de rede, liberação de acesso, reset de senha, Wi-Fi, túnel Procergs.
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `ACESSO A SISTEMAS > REDE` (id ~ 21).
- Subcategorias: `LIBERAÇÃO DE ACESSO` (22), `RESET DE SENHA` (24), `WIFI` (37), `TÚNEL PROCERGS` (33), `NOVO USUÁRIO` (35).

## Categoria ITIL alvo

- ID: `21`
- Caminho: `ACESSO A SISTEMAS > REDE`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Recomenda-se coleta específica da API do FormCreator ou ampliar parser do dump.

## Regras de Negócio

- Confirmar identidade do usuário e unidade.
- Especificar recurso de rede (pasta/serviço) e nível de acesso.
- Para túnel Procergs, validar pré-requisitos institucionais.

## Pipeline do Agente

- Extrair entidade (usuário/grupo/recurso), operação (criar/liberar/reset), e contexto.
- Selecionar subcategoria ITIL e abrir chamado com dados padronizados.

## Roteamento por Operação

- `ACESSO_PASTA` → Categoria `LIBERAÇÃO DE ACESSO` (ID 22)
- `RESET_SENHA` → Categoria `RESET DE SENHA` (ID 24)
- `CRIAR_USUARIO` → Categoria `NOVO USUÁRIO` (ID 35)
- `CRIAR_GRUPO` → Base `REDE` (ID 21)