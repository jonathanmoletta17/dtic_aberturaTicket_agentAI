# Formcreator: Lista de Formulários

Este documento lista os formulários coletados via API GLPI e normalizados em `MCP-CAU/output/formcreator_forms.json`.

## Resumo

- Total: 11 formulários
- Ativos: 8
- Inativos: 2

## Tabela

| ID | Nome                            | Ativo |
|----|---------------------------------|-------|
| 1  | EMAIL E APLICATIVOS OFFICE 365 | 1     |
| 2  | NOMEIA / EXONERA               | 1     |
| 4  | PROA-ACESSO                    | 1     |
| 5  | REQUISIÇÃO                     | 1     |
| 6  | IMPRESSORA                     | 1     |
| 7  | REDE                            | 1     |
| 8  | SISTEMAS INTERNOS              | 1     |
| 9  | INCIDENTE                      | 1     |
| 10 | INFRAESTRUTURA                 | 0     |
| 11 | Tranferência de Equipamentos   | 0     |

## Fonte

- Arquivo: `MCP-CAU/output/formcreator_forms.json`
- Script: `MCP-CAU/scripts/fetch_formcreator_forms.py`

## Observações

- O arquivo JSON já traz `id`, `name`, `is_active`; `helpdesk_name` está nulo na captura atual.
- Os nomes mapeiam para `slugs` em `config/form_schemas.json` e se relacionam às categorias descritas em `docs/10_CATALOGO_CATEGORIAS.md`.