# INFRAESTRUTURA

- Formulário: `INFRAESTRUTURA`
- GLPI Form ID: `10`
- Ativo: `0`
- Descrição: `PROBLEMA DE REDE // MUDANÇA DE LOCAL // WI-FI // NOVO PONTO DE REDE // PROJETOS`
- Uso (count): `0`
- Fonte (JSON): `../../output/forms/10_INFRAESTRUTURA.json`

## Visão Geral

- Finalidade: demandas de infraestrutura de rede (mudanças de ponto, problemas de conectividade, Wi-Fi, projetos).
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `DTIC > INFRAESTRUTURA` (id ~ 18).
- Subcategorias exemplares: PROBLEMA DE REDE (51), MUDANÇA DE LOCAL (52), NOVO PONTO DE REDE (54), PROJETOS (56).

## Categoria ITIL alvo

- ID: `18`
- Caminho: `DTIC > INFRAESTRUTURA`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Recomenda-se detalhar local, ponto de rede, equipamento e janelas de mudança.

## Regras de Negócio

- Validar janela e autorização para mudanças.
- Incluir planta/identificação de rack/ponto quando aplicável.

## Pipeline do Agente

- Classificar tipo (problema/mudança/projeto), coletar dados essenciais e abrir chamado.

## Roteamento por Operação

- `PROBLEMA_REDE` → Categoria (ID 51)
- `MUDANCA_LOCAL` → Categoria (ID 52)
- `NOVO_PONTO_REDE` → Categoria (ID 54)
- `WIFI` → Base `DTIC > INFRAESTRUTURA` (ID 18)
- `PROJETO` → Categoria (ID 56)