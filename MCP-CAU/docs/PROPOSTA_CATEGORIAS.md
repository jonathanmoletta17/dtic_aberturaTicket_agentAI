# Proposta: Sistema de Categorização de Chamados

## 🎯 Objetivo
Implementar um sistema de seleção de categorias user-friendly que mapeie para as categorias complexas do GLPI, mantendo a simplicidade para o usuário final.

## 📊 Análise da Situação Atual

### Problemas Identificados
- ✅ **Complexidade Excessiva**: 100+ categorias no GLPI
- ✅ **Nomenclatura Técnica**: Termos não familiares aos usuários
- ✅ **Estrutura Hierárquica**: Múltiplos níveis de categorização
- ✅ **Falta de Padrão**: Mistura tipos, modelos, e categorias funcionais

### Categorias GLPI Mais Relevantes para Chamados
Após análise, identifiquei as categorias mais apropriadas para chamados de usuário:

**Categorias Principais:**
- Assistência
- Categorias ITIL
- Software → Categorias de software
- Conectividade → Redes, Internet
- Tipos → Equipamentos (Computador, Impressora, Telefone, etc.)

## 🏗️ Proposta de Estrutura Simplificada

### Abordagem 1: Categorias por Tipo de Problema (Recomendada)

```yaml
Categorias User-Friendly:
├── 🖥️ HARDWARE
│   ├── Computador/Notebook
│   ├── Impressora
│   ├── Monitor
│   ├── Telefone
│   └── Outros equipamentos
├── 💻 SOFTWARE
│   ├── Sistema Operacional
│   ├── Aplicativos/Programas
│   ├── E-mail
│   └── Antivírus
├── 🌐 CONECTIVIDADE
│   ├── Internet/Rede
│   ├── WiFi
│   ├── VPN
│   └── Telefonia
├── 🔐 SEGURANÇA
│   ├── Acesso/Login
│   ├── Senhas
│   └── Permissões
├── 📋 SOLICITAÇÕES
│   ├── Instalação de software
│   ├── Criação de usuário
│   ├── Acesso a sistemas
│   └── Outros serviços
└── ❓ OUTROS
    └── Não se enquadra nas opções acima
```

### Mapeamento para GLPI

```json
{
  "HARDWARE": {
    "Computador/Notebook": "Tipos de computador",
    "Impressora": "Tipos de impressora", 
    "Monitor": "Monitor types",
    "Telefone": "Tipos de telefones",
    "Outros equipamentos": "Tipos de dispositivo"
  },
  "SOFTWARE": {
    "Sistema Operacional": "Sistemas operacionais",
    "Aplicativos/Programas": "Categorias de software",
    "E-mail": "Categorias de software",
    "Antivírus": "Categorias de software"
  },
  "CONECTIVIDADE": {
    "Internet/Rede": "Redes",
    "WiFi": "Redes WiFi", 
    "VPN": "Redes",
    "Telefonia": "Operadoras de telefonia"
  },
  "SEGURANÇA": {
    "Acesso/Login": "Categorias ITIL",
    "Senhas": "Categorias ITIL",
    "Permissões": "Categorias ITIL"
  },
  "SOLICITAÇÕES": {
    "Instalação de software": "Categorias ITIL",
    "Criação de usuário": "Categorias de usuário",
    "Acesso a sistemas": "Categorias ITIL",
    "Outros serviços": "Assistência"
  },
  "OUTROS": {
    "Não se enquadra": "Assistência"
  }
}
```

## 🔄 Implementação Proposta

### Opção 1: Seleção em Duas Etapas (Recomendada)

**Etapa 1 - Categoria Principal:**
```
🎯 Qual tipo de problema você está enfrentando?

1️⃣ HARDWARE (Computador, impressora, equipamentos)
2️⃣ SOFTWARE (Programas, sistemas, aplicativos)  
3️⃣ CONECTIVIDADE (Internet, rede, telefonia)
4️⃣ SEGURANÇA (Acesso, senhas, permissões)
5️⃣ SOLICITAÇÕES (Instalações, criações, acessos)
6️⃣ OUTROS (Não se enquadra nas opções acima)
```

**Etapa 2 - Subcategoria:**
```
📋 Especifique o tipo de hardware:

1️⃣ Computador/Notebook
2️⃣ Impressora
3️⃣ Monitor
4️⃣ Telefone
5️⃣ Outros equipamentos
```

### Opção 2: Seleção Única Simplificada

```
🎯 Selecione a categoria do seu chamado:

🖥️ HARDWARE - Computador/Notebook
🖨️ HARDWARE - Impressora  
📺 HARDWARE - Monitor
📞 HARDWARE - Telefone
💻 SOFTWARE - Aplicativos/Programas
🌐 CONECTIVIDADE - Internet/Rede
🔐 SEGURANÇA - Acesso/Login
📋 SOLICITAÇÃO - Instalação/Configuração
❓ OUTROS - Não listado acima
```

### Opção 3: Detecção Inteligente por Palavras-Chave

```python
# Mapeamento automático baseado na descrição
keywords_mapping = {
    "impressora": "HARDWARE - Impressora",
    "computador|notebook|pc": "HARDWARE - Computador",
    "internet|rede|wifi": "CONECTIVIDADE - Internet",
    "software|programa|aplicativo": "SOFTWARE - Aplicativos",
    "senha|login|acesso": "SEGURANÇA - Acesso",
    "instalar|configurar": "SOLICITAÇÃO - Instalação"
}
```

## 🎨 Implementação no Copilot Studio

### Estrutura do Fluxo Modificado

```yaml
# Novo campo de categoria antes da descrição
- kind: Question
  id: GetCategory
  alwaysPrompt: true
  variable: Topic.category_selection
  prompt: |
    🎯 **Categoria do Chamado**
    
    Selecione o tipo de problema:
    
    1️⃣ HARDWARE (equipamentos)
    2️⃣ SOFTWARE (programas)
    3️⃣ CONECTIVIDADE (rede/internet)
    4️⃣ SEGURANÇA (acesso/senhas)
    5️⃣ SOLICITAÇÕES (instalações/configurações)
    6️⃣ OUTROS
    
    Digite o número ou nome da categoria:
  entity: StringPrebuiltEntity

# Mapeamento da categoria
- kind: SetVariable
  id: MapCategory
  variable: Topic.glpi_category
  value: |
    =switch(
      Topic.category_selection,
      "1", "Tipos de computador",
      "HARDWARE", "Tipos de computador", 
      "2", "Categorias de software",
      "SOFTWARE", "Categorias de software",
      "3", "Redes",
      "CONECTIVIDADE", "Redes",
      "4", "Categorias ITIL", 
      "SEGURANÇA", "Categorias ITIL",
      "5", "Assistência",
      "SOLICITAÇÕES", "Assistência",
      "Assistência"
    )
```

## 📈 Vantagens da Abordagem

### Para o Usuário
- ✅ **Simplicidade**: Máximo 6 opções principais
- ✅ **Linguagem Natural**: Termos familiares
- ✅ **Rapidez**: Seleção em 1-2 cliques
- ✅ **Flexibilidade**: Opção "OUTROS" para casos especiais

### Para o Sistema
- ✅ **Mapeamento Direto**: Cada seleção mapeia para categoria GLPI
- ✅ **Manutenibilidade**: Fácil ajustar mapeamentos
- ✅ **Rastreabilidade**: Log de categorias selecionadas
- ✅ **Escalabilidade**: Pode expandir subcategorias

## 🚀 Próximos Passos

### Fase 1: Implementação Básica
1. **Implementar Opção 2** (seleção única simplificada)
2. **Testar com usuários reais**
3. **Ajustar mapeamentos conforme feedback**

### Fase 2: Refinamento
1. **Adicionar detecção inteligente** (Opção 3)
2. **Implementar subcategorias** se necessário
3. **Otimizar baseado em métricas de uso**

### Fase 3: Avançado
1. **Machine Learning** para sugestão automática
2. **Análise de padrões** de categorização
3. **Integração com base de conhecimento**

## 💡 Recomendação Final

**Implementar Opção 2** como ponto de partida:
- Simples e efetiva
- Fácil de implementar
- Permite evolução gradual
- Mantém compatibilidade com GLPI

Após validação com usuários, evoluir para soluções mais sofisticadas conforme necessidade.

---

**Status**: 📋 Proposta para Avaliação
**Próximo Passo**: Implementação da seleção de categoria no agente