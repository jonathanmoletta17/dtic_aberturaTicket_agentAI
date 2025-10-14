# IMPRESSORA

- Formulário: `IMPRESSORA`
- GLPI Form ID: `6`
- Ativo: `1`
- Descrição: `Problemas no equipamento de impressão`
- Uso (count): `266`
- Fonte (JSON): `../../output/forms/6_IMPRESSORA.json`

## Visão Geral

- Finalidade: incidentes e solicitações relacionadas a impressoras (instalação, atolamento, troca de toner, movimentações físicas).
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Caminhos comuns:
  - `IMPRESSORA` (id ~ 14)
  - `DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA` (id ~ 15)
- Subcategorias úteis: `ATOLAMENTO` (57), `TROCA DE TONNER` (71), `MOVIMENTAÇÃO FISICA` (72).

## Categoria ITIL alvo

- ID: `14`
- Caminho: `IMPRESSORA`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário. Usar coleta futura da API ou ampliar parser do dump.

## Regras de Negócio

- Verificar modelo, patrimônio e localização da impressora.
- Incluir descrição do problema e foto/log quando aplicável.
- Classificar como incidente ou requisição conforme a ação solicitada.

## Pipeline do Agente

- Classificar tipo de demanda (instalação, incidente, troca de insumo).
- Normalizar informações (equipamento, local, contato).
- Roteamento para categoria ITIL adequada.

## Roteamento por Operação

- `INSTALACAO` → `DTIC > EQUIPAMENTOS > INSTALAÇÃO > IMPRESSORA` (ID 15)
- `ATOLAMENTO` → Categoria (ID 57)
- `TROCA_TONNER` → Categoria (ID 71)
- `MOVIMENTACAO_FISICA` → Categoria (ID 72)