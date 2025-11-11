# Padrão HTTP → ParseJSON para tópicos do Copilot

Objetivo: eliminar erros comuns de tipo (ponto aplicado em `Text`, `Any` inválido, argumentos incorretos de `Boolean()`, `IsBlank()`, `Text()`, uso de `JsonStringify`) ao consumir respostas HTTP em tópicos.

## Fluxo recomendado

- Salvar resposta HTTP como `String` (crua).
- Converter a `String` para `UntypedObject` com `ParseJSON()`.
- Acessar propriedades do objeto parseado com ponto e conversões explícitas: `Text()`, `Boolean()`, `Value()`.
- Exportar a resposta final como `String` usando `JSON()` quando necessário.

## Passos

1) Nó HTTP
- Tipo de dados da resposta: `String`
- Salvar resposta como: `Topic.authJson` (`String`)

2) Após o HTTP
- Criar um nó “Definir valor da variável”:
  - Variável: `Topic.authObj` (`Object`)
  - Valor: `=ParseJSON(Topic.authJson)`

3) Condição de sucesso
- Usar o objeto parseado:
```
=Or(
  Boolean(Topic.authObj.sucesso),
  Boolean(Topic.authObj.success)
)
```
- Se o backend às vezes manda strings "true"/"false", pode optar por:
```
=Or(
  Boolean(Topic.authObj.sucesso) = true,
  Boolean(Topic.authObj.success) = true
)
```

4) Nós “Definir valor da variável” abaixo da condição
- Selecionar a variável alvo e usar conversões explícitas:
```
varUserName = If(
  Not(IsBlank(Text(Topic.authObj.usuario.name))),
  Text(Topic.authObj.usuario.name),
  Text(Topic.authObj.usuario.login)
)

varUserEmail = Text(Topic.authObj.usuario.email)
varUserIdGLPI = Text(Topic.authObj.usuario.id)

varApiStatus (sucesso) = "success"
varApiStatus (erro)    = "error"

varApiErrorMessage = If(
  Not(IsBlank(Text(Topic.authObj.erro))),
  Text(Topic.authObj.erro),
  If(
    Not(IsBlank(Text(Topic.authObj.error))),
    Text(Topic.authObj.error),
    "(erro nao especificado)"
  )
)
```

5) Espelhar resposta para saída do tópico
- Antes do “Encerrar o tópico”, definir a saída `authResponse` (`String`):
```
authResponse = JSON(Topic.authObj, JSONFormat.Compact)
```

6) Variáveis no tópico (tipos)
- `Topic.authJson`: `String`
- `Topic.authObj`: `Object` (recebe `UntypedObject` de `ParseJSON()`)
- `authResponse` no `outputType`: `String`

## Por que isso elimina os erros
- O ponto volta a funcionar porque é aplicado em `UntypedObject`/`Object`, não em texto.
- `Boolean()`, `Text()`, `IsBlank()` recebem tipos corretos (propriedades específicas).
- `JSON()` é a função suportada em Power Fx; evitar `JsonStringify`.
- Todos os nós “Definir valor da variável” têm variável alvo, evitando `InvalidPropertyPath`.

## Checklist rápido
- Salvar HTTP em `String` → `ParseJSON` → usar `Text`/`Boolean`/`Value` nos campos.
- Nunca usar `JsonStringify`. Usar `JSON()`.
- Sempre selecionar a variável alvo em “Definir valor da variável”.
- Evitar `Text()` sobre objetos inteiros; aplicar somente sobre a propriedade.

## Referências
- Power Fx: JSON, ParseJSON, tipos não tipados: https://learn.microsoft.com/power-platform/power-fx/reference/function-parsejson
- Power Fx: conversões `Text()`, `Value()`, `Boolean()` e `IsBlank()`: https://learn.microsoft.com/power-platform/power-fx/reference/function-text