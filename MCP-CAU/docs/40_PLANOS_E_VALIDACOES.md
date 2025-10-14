# Planos, Políticas e Validações

## Políticas de Abertura
- `requesttypes_id`: padrão 1.
- `entities_id`: usar entidade ativa configurada via `changeActiveEntities`.
- `urgency`/`priority`: definir tabela por categoria (futuro).

## Observabilidade
- Registrar resumo da classificação, campos extraídos e payload enviado.
- Armazenar `ticket_id` e tempo de resposta.

## Backlog
- Coletar IDs reais de categorias e atualizar `config/form_schemas.json`.
- Mapear todas as opções de `service_type` em EMAIL_APPS_365.
- Definir anexos e limites.
- Definir regras de roteamento quando Formcreator ≠ `ITILCategory` 1:1.

## Testes
- Conjuntos de frases por categoria para validar classificação.
- Testes de completude de campos obrigatórios.