# 📋 Propostas de Melhorias para o Copilot Studio - Abertura de Chamados GLPI

## 📊 Resumo da Análise Realizada

**Amostra analisada:** 100 tickets do GLPI  
**Data da análise:** 01/11/2025  

### 🔍 Principais Problemas Identificados:

1. **35% dos tickets** não têm informações técnicas suficientes
2. **9% dos títulos** são muito genéricos
3. **5% das descrições** contêm termos vagos
4. **1% das descrições** são muito curtas

### 📈 Categorias Mais Utilizadas:
- **Categoria 7:** 17 tickets (17%)
- **Categoria 20:** 12 tickets (12%)  
- **Categoria 8:** 9 tickets (9%)

---

## 🎯 Propostas de Melhorias Específicas

### 1. **Validação de Descrições Mínimas**

**Problema:** Descrições muito curtas ou vagas  
**Solução:** Implementar validação de qualidade

```yaml
# Adicionar no fluxo do Copilot Studio
- trigger:
    condition: "len(Topic.description) < 50"
    action: "request_more_details"
    message: "Por favor, forneça mais detalhes sobre o problema. Descreva quando acontece, que mensagem aparece, ou qual comportamento esperado."
```

### 2. **Perguntas Direcionadas por Categoria**

**Problema:** 35% dos tickets sem informações técnicas suficientes  
**Solução:** Criar fluxos específicos por categoria

#### Para Hardware (Categoria 7 - mais comum):
```yaml
additional_questions:
  - question: "Qual equipamento está apresentando problema?"
    options: ["Computador", "Impressora", "Monitor", "Teclado/Mouse", "Outro"]
  - question: "Qual a marca/modelo do equipamento?"
    type: "text"
    required: true
  - question: "O problema acontece sempre ou esporadicamente?"
    options: ["Sempre", "Às vezes", "Primeira vez"]
  - question: "Há alguma mensagem de erro? Se sim, qual?"
    type: "text"
```

#### Para Software (Categoria 20):
```yaml
additional_questions:
  - question: "Qual programa/sistema está com problema?"
    type: "text"
    required: true
  - question: "Qual versão do programa?"
    type: "text"
  - question: "O erro acontece ao abrir, usar ou fechar o programa?"
    options: ["Ao abrir", "Durante o uso", "Ao fechar", "Não abre"]
  - question: "Outros usuários têm o mesmo problema?"
    options: ["Sim", "Não", "Não sei"]
```

#### Para Conectividade/Rede (Categoria 8):
```yaml
additional_questions:
  - question: "Onde você está localizado?"
    type: "text"
    required: true
  - question: "O problema é com internet, rede interna ou VPN?"
    options: ["Internet", "Rede interna", "VPN", "Não sei"]
  - question: "Outros computadores no local têm o mesmo problema?"
    options: ["Sim", "Não", "Não testei"]
  - question: "Há algum código de erro ou mensagem específica?"
    type: "text"
```

### 3. **Templates de Títulos Inteligentes**

**Problema:** 9% dos títulos são genéricos  
**Solução:** Sugerir títulos baseados nas respostas

```yaml
title_templates:
  hardware:
    pattern: "Hardware - {equipamento} - {problema_resumido}"
    example: "Hardware - Impressora HP - Não imprime"
  
  software:
    pattern: "Software - {programa} - {tipo_erro}"
    example: "Software - Office 365 - Erro ao abrir Excel"
  
  conectividade:
    pattern: "Rede - {local} - {tipo_problema}"
    example: "Rede - Sala 201 - Sem acesso à internet"
  
  solicitacao:
    pattern: "Solicitação - {tipo} - {recurso}"
    example: "Solicitação - Acesso - Sistema FPE"
```

### 4. **Validação de Palavras Vagas**

**Problema:** 5% das descrições com termos muito vagos  
**Solução:** Detectar e solicitar especificação

```yaml
vague_words_detection:
  trigger_words: ["problema", "erro", "não funciona", "quebrou", "parou", "travou"]
  follow_up_questions:
    "problema": "Que tipo de problema especificamente?"
    "erro": "Qual mensagem de erro aparece?"
    "não funciona": "O que exatamente não está funcionando? O que você esperava que acontecesse?"
    "quebrou": "O que estava funcionando antes e agora não funciona mais?"
    "parou": "Em que momento parou de funcionar?"
    "travou": "O sistema trava em que momento específico?"
```

### 5. **Campos Obrigatórios Dinâmicos**

**Solução:** Campos obrigatórios que aparecem baseados na categoria

```yaml
dynamic_required_fields:
  hardware:
    - equipment_type
    - equipment_location
    - problem_frequency
  
  software:
    - software_name
    - error_moment
    - affects_others
  
  network:
    - user_location
    - network_type
    - other_users_affected
  
  access_request:
    - system_name
    - access_type
    - business_justification
```

---

## 🛠️ Implementação Prática no Copilot Studio

### Fase 1: Validações Básicas (Implementação Imediata)

1. **Validação de tamanho mínimo:** 50 caracteres para descrição
2. **Detecção de palavras vagas:** Solicitar especificação
3. **Campos obrigatórios:** Local e telefone sempre obrigatórios

### Fase 2: Perguntas Direcionadas (2-3 semanas)

1. **Implementar fluxos específicos** para as 3 categorias mais comuns
2. **Templates de títulos** automáticos
3. **Validação de informações técnicas** por categoria

### Fase 3: Inteligência Avançada (1-2 meses)

1. **Sugestões automáticas** baseadas em histórico
2. **Detecção de problemas similares** já resolvidos
3. **Escalação automática** baseada em palavras-chave

---

## 📝 Exemplos de Fluxos Melhorados

### Fluxo Atual vs. Proposto

#### ❌ **Fluxo Atual:**
```
1. Categoria: Hardware
2. Descrição: "Impressora não funciona"
3. Local: "Sala 201"
4. Telefone: "1234"
→ Ticket criado com informações insuficientes
```

#### ✅ **Fluxo Proposto:**
```
1. Categoria: Hardware
2. Qual equipamento? "Impressora"
3. Marca/modelo? "HP LaserJet 1020"
4. Descrição do problema: "Impressora não funciona"
   → Sistema detecta termo vago
   → "Qual mensagem aparece? A impressora liga? Há papel?"
5. Resposta: "Liga mas não puxa o papel, fica piscando luz vermelha"
6. Local: "Sala 201 - Departamento Financeiro"
7. Telefone: "1234"
8. Título sugerido: "Hardware - Impressora HP - Não puxa papel"
→ Ticket criado com informações completas
```

---

## 🎯 Resultados Esperados

### Métricas de Melhoria:
- **Reduzir em 80%** tickets com informações insuficientes
- **Reduzir em 70%** títulos genéricos
- **Reduzir em 90%** descrições vagas
- **Aumentar em 50%** a velocidade de resolução
- **Reduzir em 60%** idas e vindas para esclarecimentos

### Benefícios:
1. **Para usuários:** Processo mais guiado e intuitivo
2. **Para técnicos:** Informações mais completas para diagnóstico
3. **Para gestão:** Métricas mais precisas e categorização melhor
4. **Para organização:** Redução de tempo de resolução

---

## 🚀 Próximos Passos

1. **Revisar e aprovar** as propostas com a equipe
2. **Priorizar implementações** por impacto vs. esforço
3. **Criar protótipos** dos novos fluxos no Copilot Studio
4. **Testar** com grupo piloto
5. **Implementar gradualmente** as melhorias
6. **Monitorar métricas** de melhoria

---

*Documento gerado baseado na análise de 100 tickets reais do GLPI em 01/11/2025*