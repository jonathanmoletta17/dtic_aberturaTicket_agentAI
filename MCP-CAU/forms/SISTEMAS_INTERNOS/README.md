# SISTEMAS_INTERNOS

- Formulário: `SISTEMAS INTERNOS`
- GLPI Form ID: `8`
- Ativo: `1`
- Descrição: `LIBERAR/REMOVER ACESSO ,DESBLOQUEAR USUÁRIO, Sistemas -AFE ,Agenda , FPE, GCE, GDG, LAI, RHE, SGM, SPI, Túnel PROCERGS`
- Uso (count): `1131`
- Fonte (JSON): `../../output/forms/8_SISTEMAS_INTERNOS.json`

## Visão Geral

- Finalidade: operações em sistemas internos (acessos, desbloqueios, configurações).
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `DTIC > SISTEMAS` (id ~ 40).
- Subcategorias: `INSTALAÇÃO DE SOFTWARE` (46), `CONFIGURAÇÃO DE SOFTWARE` (47), `ALTERAÇÃO DE ACESSO` (49), `REMOÇÃO DE ACESSO SISTEMA` (48).

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Campos esperados: sistema alvo, usuário, operação (liberar/remover), justificativa.

## Regras de Negócio

- Validar política de acesso por sistema.
- Registrar aprovação quando necessário.

## Pipeline do Agente

- Identificar sistema e operação, mapear categoria e abrir chamado com evidências.

## Roteamento por Operação

- `INSTALAÇÃO DE SOFTWARE` → Categoria (ID 46)
- `CONFIGURAÇÃO DE SOFTWARE` → Categoria (ID 47)
- `ALTERAÇÃO DE ACESSO` → Categoria (ID 49)
- `REMOÇÃO DE ACESSO SISTEMA` → Categoria (ID 48)
- `DESBLOQUEAR USUÁRIO` → Base `DTIC > SISTEMAS` (ID 40)