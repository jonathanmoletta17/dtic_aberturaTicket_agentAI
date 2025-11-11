# Sanitização de YAML para Copilot Studio

Problemas comuns de parsing no Copilot Studio:
- Tabs misturados com espaços.
- CRLF em vez de LF.
- Caracteres invisíveis (NBSP, hífen especial) em chaves/valores.
- Indentação irregular em blocos literais (`|`/`|-`).
- Espaços à direita e linhas em branco com espaços.

## Checklist de sanitização
- Normalize espaços: apenas espaços comuns, sem NBSP.
- Converter tabs → 2 espaços.
- Quebras de linha: usar LF.
- Remover espaços à direita em todas as linhas.
- Indentação consistente: 2 espaços por nível.
- Em `content: |-` garantir indentação exata e sem linhas “soltas”.
- Tipos consistentes: preferir `String`, `Object`, `Any` em schemas; nas `variables` usar a mesma convenção (maiúsculas). Se persistir erro, padronizar tudo em `String`/`Object`.

## Boas práticas
- Evite copiar/colar de editores que introduzem NBSP/hífens especiais.
- Revise blocos literais após qualquer edição.
- Valide YAML após mudanças significativas (script de lint).

## Referências
- Solução de problemas do Copilot Studio Kit (Microsoft Learn): https://learn.microsoft.com/pt-br/microsoft-copilot-studio/guidance/kit-troubleshoot
- Configurar autenticação do usuário (Microsoft Learn): https://learn.microsoft.com/pt-br/microsoft-copilot-studio/configuration-end-user-authentication
- Códigos de erro do Copilot Studio (Microsoft Learn): https://learn.microsoft.com/pt-br/microsoft-copilot-studio/error-codes