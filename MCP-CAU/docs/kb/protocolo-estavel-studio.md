# Protocolo estável para edição de tópicos do Copilot Studio

Este protocolo evita o “ciclo de quebra” causado pela mistura de camadas (YAML vs Power Fx), normalização invisível e alternância de convenções. Siga a ordem abaixo, sem pular etapas.

## Ambiente de edição
- Use VS Code ou Notepad++.
- Configurações: UTF-8 sem BOM, LF; renderizar espaços e mostrar caracteres de controle.
- Desative smart quotes e substituições automáticas do SO/teclado.

## Sanitização antes de colar no Studio
- Remova NBSP (\u00A0) e TAB (\t).
- Primeira rodada: somente ASCII; sem emojis, sem acentos, sem hífen não-ASCII.
- Evite `|` e blocos literais na primeira rodada; prefira mensagens diretas.
- 2 espaços por nível; nova linha ao final do arquivo.

## Separação de responsabilidades
- YAML: somente estrutura do tópico, nomes de variáveis e tipos.
- Power Fx: edite fórmulas no designer, não no YAML. Assim o Studio valida por nó e evita quebrar o arquivo inteiro.

## Tipos e escopo
- `Topic.*` é local; não exporte brutos.
- Saídas: defina em `outputType` sem ponto no nome (ex.: `authResponse`).
- JSON de HTTP: `String (Topic.authJson)` → `ParseJSON` → `Object (Topic.authObj)`.
- Em fórmulas: use `Text()/Boolean()/Value()` sobre propriedades de `Topic.authObj`.

## Mudanças atômicas
- Aplique um patch pequeno por vez.
- Salve → Verificador de tópico → só então aplique o próximo.
- Nunca cole o arquivo completo depois que o designer organizou nós.

## Teste mínimo e localização de defeitos
- Se o erro estiver “near last line”:
  - Procure primeiro bloco com `|`/`-` mal indentado.
  - Procure primeira fórmula com ponto em `String` (falta `ParseJSON` ou `Text()` na propriedade).
  - Procure primeira linha com caractere não-ASCII.
- Mensagens comuns:
  - “PowerFxError: operador ‘.’ em Text”: falta `ParseJSON` ou conversão por propriedade.
  - “Boolean inválido”: converta o campo com `Boolean(obj.flag)` ou com `Value(Text(...))`.
  - “InvalidPropertyPath” no “Definir valor da variável”: selecione a variável alvo.

## Controle de regressão
- Mantenha um baseline sem emojis/pipes.
- Reintroduza cosméticos pelo designer, não no YAML bruto.

## Ferramentas de apoio
- `.editorconfig` força LF, UTF-8, 2 espaços, newline final.
- `.prettierrc` padroniza largura de tabulação e EOL.
- `.yamllint` valida indentação, trailing spaces, newline final, desativa truthy.
- `.vscode/settings.json` aplica encoding/EOL e renderização de invisíveis.
- `scripts/lint_yaml_copilot.py` detecta NBSP/TAB/CRLF/BOM/trailing spaces/não-ASCII e inconsistências de tipo (`String` vs `string`, etc.).

### Validação local rápida
- CLI (qualquer um):
  - `yamllint seu_topico.yaml`
  - `yarn add -D yaml-lint && npx yaml-lint seu_topico.yaml`
  - `pip install ruamel.yaml && python -c "import sys,ruamel.yaml as y; y.YAML().load(open(sys.argv[1]))" seu_topico.yaml`

### Caça a invisíveis no VS Code
- NBSP: `\u00A0`
- Qualquer não-ASCII: `[^\x00-\x7F]`
- TAB: `\t`
Habilite “Use Regular Expression” na busca.

### Snippets úteis
- Substituir NBSP por espaço:
  - VS Code: Find `\u00A0` → Replace ` `
  - Python: `open(f).read().replace('\u00A0',' ')`
- Converter CRLF → LF: status bar VS Code (mude “CRLF” para “LF”).
- Remover BOM: salve como “UTF-8” (sem BOM).

## Referências
- Power Fx: ParseJSON/JSON e conversões: https://learn.microsoft.com/power-platform/power-fx/reference/function-parsejson
- Boas práticas e estrutura YAML (docs internos do projeto).