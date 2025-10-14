# 🎫 Ticket AI - Sistema Simples de Abertura de Tickets GLPI

## 🎯 **OBJETIVO**
Sistema **MÍNIMO e OBJETIVO** para abertura automática de tickets no GLPI usando Inteligência Artificial.

## ⚡ **COMO FUNCIONA**
1. **Usuário escreve** o problema em linguagem natural
2. **IA processa** e extrai informações (categoria, prioridade, título)
3. **Sistema cria** ticket automaticamente no GLPI

## 🚀 **INSTALAÇÃO RÁPIDA**

### 1. Instalar Dependências
```bash
cd MCP-CAU
pip install -r requirements.txt
```

### 2. Configurar GLPI
```bash
# Copie e configure o arquivo .env
copy .env.example .env
```

Edite o `.env` com suas credenciais:
```
API_URL=http://seu.glpi/apirest.php
APP_TOKEN=seu_app_token
USER_TOKEN=seu_user_token
```

### 3. Executar Sistema
```bash
python app.py
```

### 4. Acessar Interface
Abra: `http://localhost:5000`

## 🧠 **INTELIGÊNCIA ARTIFICIAL**

### **Extração Automática:**
- **Prioridade**: Detecta palavras como "urgente", "crítico", "normal"
- **Categoria**: Identifica tipo (email, impressora, rede, sistema, etc.)
- **Título**: Usa primeira linha ou primeiros 50 caracteres
- **Conteúdo**: Texto completo da solicitação

### **Exemplos de Uso:**
```
"Meu email não está funcionando, não consigo enviar mensagens"
→ Categoria: EMAIL, Prioridade: MÉDIA

"A impressora da sala 205 está com problema urgente"
→ Categoria: IMPRESSORA, Prioridade: ALTA

"Preciso de acesso ao sistema interno da empresa"
→ Categoria: ACESSO, Prioridade: MÉDIA
```

## 📋 **ESTRUTURA DO PROJETO**

```
MCP-CAU/
├── app.py                 # API principal Flask
├── templates/
│   └── index.html        # Interface web
├── requirements.txt      # Dependências Python
├── .env                 # Configurações (criar)
└── output/
    ├── itil_categories.json    # Categorias GLPI
    └── formcreator_forms.json  # Formulários
```

## 🔧 **API ENDPOINTS**

### `POST /api/create-ticket`
Cria ticket via IA
```json
{
  "text": "Descrição do problema em linguagem natural"
}
```

### `GET /api/test-connection`
Testa conexão com GLPI

### `GET /api/categories`
Lista categorias disponíveis

## ✅ **VANTAGENS DESTA SOLUÇÃO**

1. **SIMPLES**: Apenas 3 arquivos principais
2. **RÁPIDA**: Instalação em 5 minutos
3. **INTELIGENTE**: Processa linguagem natural
4. **VISUAL**: Interface web amigável
5. **EXTENSÍVEL**: Fácil de personalizar

## 🎨 **PERSONALIZAÇÃO**

### Adicionar Novas Categorias:
Edite a função `extract_category()` em `app.py`

### Modificar Prioridades:
Edite a função `extract_priority()` em `app.py`

### Customizar Interface:
Modifique `templates/index.html`

## 🔍 **TROUBLESHOOTING**

### Erro de Conexão GLPI:
- Verifique credenciais no `.env`
- Confirme se API REST está habilitada no GLPI
- Teste endpoint manualmente

### Erro de Categoria:
- Verifique se `itil_categories.json` existe
- Confirme IDs das categorias no GLPI

## 📞 **SUPORTE**
Sistema criado para ser **MÍNIMO e FUNCIONAL**. Para expansões, considere:
- Integração com modelos de IA mais avançados
- Processamento de anexos
- Notificações automáticas
- Dashboard de métricas