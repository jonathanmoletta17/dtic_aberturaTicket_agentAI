# INCIDENTE

- Formulário: `INCIDENTE`
- GLPI Form ID: `9`
- Ativo: `1`
- Descrição: `Problemas com Equipamento/Rede/Outros`
- Uso (count): `407`
- Fonte (JSON): `../../output/forms/9_INCIDENTE.json`

## Visão Geral

- Finalidade: registro de incidentes em equipamentos, rede e serviços.
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Base: `AJUDA E SUPORTE` (id ~ 7).
- Incidentes de rede: `DTIC > INFRAESTRUTURA > PROBLEMA DE REDE` (id ~ 51).

## Categoria ITIL alvo

- ID: `7`
- Caminho: `AJUDA E SUPORTE`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Recolher informações mínimas: título, descrição, equipamento, local, impacto.

## Regras de Negócio

- Classificar prioridade conforme impacto/urgência.
- Vincular a equipamento ou serviço quando possível.
- Direcionar para equipe responsável conforme categoria.

## Pipeline do Agente

- Extrair sintomas, escopo e impacto.
- Normalizar dados e abrir incidente com categoria apropriada.