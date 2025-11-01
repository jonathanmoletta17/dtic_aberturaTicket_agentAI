# Documentação do Sistema de Categorização de Chamados

## Visão Geral

Este documento descreve o sistema de categorização implementado para simplificar a seleção de categorias de chamados no agente AI integrado com GLPI.

## Problema Resolvido

O GLPI possui uma estrutura complexa de categorias e subcategorias que pode confundir os usuários finais. O sistema implementado resolve isso através de:

- **Categorias User-Friendly**: 8 categorias simples e intuitivas
- **Mapeamento Automático**: Conversão automática para categorias GLPI
- **Interface Simplificada**: Seleção em um único clique

## Categorias Implementadas

### 1. HARDWARE_COMPUTADOR
- **Descrição**: Problemas com computadores e notebooks
- **Categoria GLPI**: `Categorias de hardware`
- **Subcategoria GLPI**: `Computador`
- **Exemplos**: Computador não liga, tela azul, lentidão

### 2. HARDWARE_IMPRESSORA
- **Descrição**: Problemas com impressoras
- **Categoria GLPI**: `Categorias de hardware`
- **Subcategoria GLPI**: `Impressora`
- **Exemplos**: Impressora não imprime, papel atolado, toner

### 3. HARDWARE_MONITOR
- **Descrição**: Problemas com monitores e equipamentos
- **Categoria GLPI**: `Categorias de hardware`
- **Subcategoria GLPI**: `Monitor`
- **Exemplos**: Monitor sem imagem, cabo defeituoso

### 4. SOFTWARE
- **Descrição**: Problemas com aplicativos e programas
- **Categoria GLPI**: `Categorias de software`
- **Subcategoria GLPI**: `Aplicativo`
- **Exemplos**: Programa não abre, erro de instalação, licença

### 5. CONECTIVIDADE
- **Descrição**: Problemas de internet e rede
- **Categoria GLPI**: `Categorias de rede`
- **Subcategoria GLPI**: `Internet`
- **Exemplos**: Sem internet, Wi-Fi lento, cabo de rede

### 6. SEGURANCA
- **Descrição**: Problemas de acesso e login
- **Categoria GLPI**: `Categorias de segurança`
- **Subcategoria GLPI**: `Acesso`
- **Exemplos**: Esqueci senha, conta bloqueada, acesso negado

### 7. SOLICITACAO
- **Descrição**: Solicitações de instalação e configuração
- **Categoria GLPI**: `Categorias de solicitação`
- **Subcategoria GLPI**: `Instalação`
- **Exemplos**: Instalar programa, configurar email, novo usuário

### 8. OUTROS
- **Descrição**: Outros problemas não categorizados
- **Categoria GLPI**: `INCIDENTE`
- **Subcategoria GLPI**: Não aplicável
- **Exemplos**: Problemas diversos, dúvidas gerais

## Implementação Técnica

### Arquivos Modificados

1. **AbrirChamado.mcs.yml**
   - Adicionada pergunta `GetCategory` antes da descrição
   - Configuradas 8 opções de categoria
   - Variável `Topic.category_user_friendly` para armazenar seleção

2. **app.py**
   - Adicionado dicionário `CATEGORY_MAP` com mapeamentos
   - Criada função `mapear_categoria()` para conversão
   - Integração na função `create_ticket_complete()`

### Fluxo de Funcionamento

```
1. Usuário seleciona categoria user-friendly
   ↓
2. Sistema armazena em Topic.category_user_friendly
   ↓
3. Dados enviados para backend via HTTP
   ↓
4. Backend mapeia categoria usando CATEGORY_MAP
   ↓
5. Categoria GLPI é usada na criação do ticket
   ↓
6. Ticket criado com categoria correta no GLPI
```

### Código de Mapeamento

```python
CATEGORY_MAP = {
    'HARDWARE_COMPUTADOR': 'Categorias de hardware',
    'HARDWARE_IMPRESSORA': 'Categorias de hardware', 
    'HARDWARE_MONITOR': 'Categorias de hardware',
    'SOFTWARE': 'Categorias de software',
    'CONECTIVIDADE': 'Categorias de rede',
    'SEGURANCA': 'Categorias de segurança',
    'SOLICITACAO': 'Categorias de solicitação',
    'OUTROS': 'INCIDENTE'
}

def mapear_categoria(categoria_user_friendly):
    return CATEGORY_MAP.get(categoria_user_friendly, 'INCIDENTE')
```

## Testes Realizados

### Teste 1: HARDWARE_IMPRESSORA
- **Input**: `"category": "HARDWARE_IMPRESSORA"`
- **Output**: Categoria GLPI: `Categorias de hardware`
- **Resultado**: ✅ Ticket #11011 criado com sucesso

### Teste 2: SOFTWARE
- **Input**: `"category": "SOFTWARE"`
- **Output**: Categoria GLPI: `Categorias de software`
- **Resultado**: ✅ Ticket #11012 criado com sucesso

### Logs de Validação
```
2025-11-01 09:45:06,170 - INFO - [9d694406] Categoria original: HARDWARE_IMPRESSORA -> Categoria GLPI: Categorias de hardware
2025-11-01 09:45:15,460 - INFO - [f428de20] Categoria original: SOFTWARE -> Categoria GLPI: Categorias de software
```

## Benefícios

### Para o Usuário
- **Simplicidade**: 8 categorias claras vs. dezenas de opções GLPI
- **Intuitividade**: Nomes descritivos e familiares
- **Rapidez**: Seleção em um clique
- **Redução de Erros**: Menos chance de categoria incorreta

### Para o Sistema
- **Manutenibilidade**: Mapeamento centralizado e fácil de alterar
- **Flexibilidade**: Novos mapeamentos podem ser adicionados facilmente
- **Compatibilidade**: Mantém estrutura original do GLPI
- **Rastreabilidade**: Logs detalhados da conversão

## Configuração e Manutenção

### Adicionando Nova Categoria
1. Adicionar entrada no `CATEGORY_MAP` em `app.py`
2. Adicionar opção no `GetCategory` em `AbrirChamado.mcs.yml`
3. Testar o mapeamento
4. Atualizar documentação

### Alterando Mapeamento Existente
1. Modificar valor no `CATEGORY_MAP`
2. Testar com categoria específica
3. Verificar logs de conversão

### Monitoramento
- Verificar logs para conversões de categoria
- Acompanhar tickets criados com categorias corretas
- Validar feedback dos usuários

## Próximos Passos Sugeridos

1. **Análise de Uso**: Monitorar quais categorias são mais utilizadas
2. **Refinamento**: Ajustar mapeamentos baseado no uso real
3. **Subcategorias**: Considerar implementar seleção de subcategorias
4. **Detecção Automática**: Implementar IA para sugerir categoria baseada na descrição
5. **Relatórios**: Criar dashboards de uso por categoria

## Conclusão

O sistema de categorização implementado simplifica significativamente a experiência do usuário, mantendo a compatibilidade com a estrutura do GLPI. A implementação é robusta, testada e facilmente mantível.