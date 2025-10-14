# NOMEIA_EXONERA

- Formulário: `NOMEIA / EXONERA`
- GLPI Form ID: `2`
- Ativo: `1`
- Descrição: `Dados que devem ser fornecidos para o cadastramento junto aos sistemas de rede:`
- Uso (count): `73`
- Fonte (JSON): `../../output/forms/2_NOMEIA_EXONERA.json`

## Visão Geral

- Finalidade: cadastro e alteração de vínculo de usuários (nomeação/exoneração).
- Documentos de apoio: `docs/20_FORMULARIOS_ESQUEMA.md` e `docs/10_CATALOGO_CATEGORIAS.md`.

## Categoria ITIL (roteamento)

- Associadas a acesso a sistemas/rede, conforme serviço: `ACESSO A SISTEMAS > SOE` (id ~ 16) ou subáreas.

## Categoria ITIL alvo

- ID: `16`
- Caminho: `ACESSO A SISTEMAS > SOE`

## Campos do Formulário

- Dump SQL atual não contém campos para este formulário.
- Campos esperados: dados pessoais, unidade, perfil de acesso, datas de vigência.

## Regras de Negócio

- Validar unidade e perfil conforme política institucional.
- Registrar datas de início/fim e responsável pela solicitação.

## Pipeline do Agente

- Extrair dados de identificação e tipo de solicitação.
- Mapear categoria e abrir chamado com registro formal.

## Roteamento por Operação

- `NOMEACAO` → Base `ACESSO A SISTEMAS > SOE` (ID 16)
- `EXONERACAO` → Base `ACESSO A SISTEMAS > SOE` (ID 16)