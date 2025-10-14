# PROA_ACESSO

- Formulário: `PROA-ACESSO`
- GLPI Form ID: `4`
- Ativo: `1`
- Descrição: `Solicitação de acesso a grupo PROA`
- Uso (count): `371`
- Fonte (JSON): `../../output/forms/4_PROA_ACESSO.json`

## Visão Geral

- Finalidade: gerenciar entradas e saídas de usuários em grupos PROA.
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `ACESSO A SISTEMAS > SOE > PROA` (id ~ 17).
- Subcategorias: `ADICIONAR A GRUPO` (31), `REMOVER DE GRUPO` (30).

## Categoria ITIL alvo

- ID: `17`
- Caminho: `ACESSO A SISTEMAS > SOE > PROA`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Campos esperados: usuário, grupo alvo, justificativa, aprovação se aplicável.

## Regras de Negócio

- Verificar aprovação e trilha de auditoria.
- Aplicar prazos e revisão de acessos periodicamente.

## Pipeline do Agente

- Identificar operação (adicionar/remover), validar dados e abrir solicitação com categoria alvo.

## Roteamento por Operação

- `ADICIONAR A GRUPO` → Categoria (ID 31)
- `REMOVER DE GRUPO` → Categoria (ID 30)