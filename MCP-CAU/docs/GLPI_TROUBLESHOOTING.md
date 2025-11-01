# 🔧 GLPI Troubleshooting

## 🚨 PROBLEMA CRÍTICO IDENTIFICADO - Permissões de Usuário

**DATA:** 01/11/2025 09:12  
**STATUS:** ❌ BLOQUEADOR  

### 📋 Resumo do Problema Atual

**ERRO GLPI:**
```
["ERROR_GLPI_ADD","Você não tem permissão para executar essa ação."]
```

**SITUAÇÃO ATUAL:**
- ✅ API está funcionando corretamente
- ✅ Validações de campos obrigatórios funcionando (46.7% de sucesso nos testes)
- ✅ Autenticação no GLPI bem-sucedida
- ✅ Payload formatado corretamente
- ❌ **BLOQUEADOR:** Usuário não tem permissão para criar tickets

### 🔍 Logs Detalhados
```
2025-11-01 09:12:52,721 - INFO - Payload enviado ao GLPI: {
  'input': {
    'name': 'Ticket de Teste',
    'content': 'Teste de ticket\\n\\nLocal: Sala 101\\n\\nTelefone: 51999999999\\n\\nCategoria: Hardware',
    'type': 1,
    'urgency': 2,
    'impact': 2,
    'priority': 2,
    'status': 2,
    'entities_id': 0
  }
}
2025-11-01 09:12:52,772 - INFO - Status da resposta GLPI: 400
2025-11-01 09:12:52,772 - INFO - Resposta GLPI: ["ERROR_GLPI_ADD","Você não tem permissão para executar essa ação."]
```

### 🛠️ Soluções Necessárias

1. **Verificar Perfil do Usuário no GLPI:**
   - Acessar: `Administração > Usuários > [Usuário do Token]`
   - Verificar se o perfil tem permissão para "Criar tickets"

2. **Verificar Entidade (entities_id):**
   - O `entities_id: 0` pode não ser válido
   - Verificar entidades disponíveis para o usuário

3. **Verificar Permissões do Token:**
   - Token pode estar limitado a operações de leitura
   - Verificar se o token tem permissões de escrita

4. **Configurar Perfil Adequado:**
   - Criar/atribuir perfil com permissões para criação de tickets
   - Verificar permissões específicas para a API REST

---

## 📋 Problema Anterior - Campos não exibidos (RESOLVIDO)

**SITUAÇÃO ANTERIOR:**
- ✅ API estava funcionando corretamente
- ✅ Dados estavam sendo enviados corretamente ao GLPI
- ✅ GLPI estava persistindo todos os campos (verificado via API)
- ❌ Interface do GLPI não estava exibindo descrição e prioridade

## 🔍 Verificações Realizadas

### 1. Teste da API Local
```bash
# Teste realizado com sucesso
POST /api/create-ticket-complete
{
  "category": "INCIDENTE",
  "description": "Printer not working",
  "impact": "MEDIO",
  "location": "Office",
  "title": "Chamado via Copilot Studio"
}
# ✅ Resultado: Ticket #10970 criado com sucesso
```

### 2. Teste Direto na API do GLPI
```json
{
  "input": {
    "name": "TESTE - Chamado via API Direta",
    "content": "Esta é uma descrição de teste...",
    "urgency": 4,
    "impact": 4,
    "priority": 4,
    "itilcategories_id": 7,
    "type": 1,
    "status": 1
  }
}
```
**✅ Resultado:** Todos os campos foram persistidos corretamente no GLPI (ID: 10971)

## 🎯 Possíveis Causas do Problema

### 1. **Configuração de Exibição de Campos**
O GLPI pode ter configurações que ocultam certos campos na interface:

**📍 Verificar em:** `Configuração > Geral > Exibição`
- Verificar se os campos `content`, `urgency`, `impact`, `priority` estão habilitados para exibição
- Verificar configurações de "Campos visíveis" para tickets

### 2. **Perfil de Usuário**
Seu perfil pode não ter permissão para visualizar todos os campos:

**📍 Verificar em:** `Administração > Perfis > [Seu Perfil] > Assistência`
- Verificar permissões para "Ticket"
- Verificar se pode visualizar campos como "Conteúdo", "Urgência", "Impacto", "Prioridade"

### 3. **Layout da Tela de Ticket**
O layout pode estar configurado para não exibir esses campos:

**📍 Verificar em:** Ao abrir um ticket
- Clicar em "Personalizar" ou "Configurar exibição"
- Verificar se os campos estão marcados para exibição
- Adicionar campos se necessário

### 4. **Versão do GLPI**
Algumas versões podem ter bugs ou comportamentos diferentes:

**📍 Verificar:** `Configuração > Geral > Informações gerais`
- Anotar a versão do GLPI
- Verificar se há atualizações disponíveis

## 🔧 Passos para Resolução

### Passo 1: Verificar Ticket Específico
1. Acesse o GLPI
2. Vá em `Assistência > Tickets`
3. Busque pelo ticket **#10971** (criado pelo teste)
4. Abra o ticket e verifique se consegue ver:
   - **Título:** "TESTE - Chamado via API Direta"
   - **Descrição/Conteúdo:** "Esta é uma descrição de teste..."
   - **Urgência:** Alto (4)
   - **Impacto:** Alto (4)
   - **Prioridade:** Alto (4)

### Passo 2: Configurar Exibição de Campos
1. No ticket aberto, procure por:
   - Botão "Personalizar" ou "Configurar exibição"
   - Menu de contexto (três pontos)
   - Opções de layout
2. Adicione os campos que não estão aparecendo:
   - Conteúdo/Descrição
   - Urgência
   - Impacto
   - Prioridade

### Passo 3: Verificar Permissões
1. Vá em `Administração > Perfis`
2. Encontre seu perfil atual
3. Vá na aba `Assistência`
4. Verifique as permissões para "Ticket"
5. Certifique-se de que pode "Ler" todos os campos

### Passo 4: Verificar Configurações Globais
1. Vá em `Configuração > Geral > Exibição`
2. Procure por configurações relacionadas a tickets
3. Verifique se há campos desabilitados

## 📊 Dados de Teste para Verificação

### Tickets Criados para Teste:
- **#10970:** Criado via API local (Copilot Studio)
- **#10971:** Criado via API direta (teste manual)

### Campos que DEVEM estar visíveis:
- **Nome/Título:** ✅ Funcionando
- **Conteúdo/Descrição:** ❌ Não aparece na interface
- **Urgência:** ❌ Não aparece na interface  
- **Impacto:** ❌ Não aparece na interface
- **Prioridade:** ❌ Não aparece na interface

## 🚀 Próximos Passos

1. **Verificar os tickets de teste no GLPI**
2. **Configurar exibição dos campos faltantes**
3. **Testar novamente com o Copilot Studio**
4. **Confirmar que todos os campos aparecem corretamente**

## 📞 Suporte Adicional

Se após essas verificações o problema persistir, pode ser necessário:
- Contatar administrador do GLPI
- Verificar logs do GLPI
- Revisar configurações de banco de dados
- Considerar atualização do GLPI

---

**💡 IMPORTANTE:** O problema NÃO está na nossa aplicação ou integração. Todos os dados estão sendo enviados e persistidos corretamente no GLPI. O problema é apenas de exibição na interface.