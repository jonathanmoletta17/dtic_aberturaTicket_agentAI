# 🚀 Guia de Configuração - Agente Copilot Studio

## 📋 Visão Geral

Este projeto implementa um agente para Microsoft Copilot Studio que cria tickets no GLPI através de uma API Flask simples e eficiente.

## ⚡ Configuração Rápida

### 1. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
# Configurações do GLPI
GLPI_URL=http://seu-glpi.com/apirest.php
GLPI_APP_TOKEN=seu_app_token_aqui
GLPI_USER_TOKEN=seu_user_token_aqui
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a API

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## 🔧 Configuração no Copilot Studio

### Importar o Tópico

1. No Copilot Studio, vá para **Topics** (Tópicos)
2. Clique em **+ New topic** (Novo tópico)
3. Escolha **From YAML** (Do YAML)
4. Cole o conteúdo do arquivo `copilot-create-ticket-config.yaml`
5. Clique em **Save** (Salvar)

### Configurar HTTP Request

O tópico já vem configurado com:
- **URL**: `http://localhost:5000/api/create-ticket-complete`
- **Método**: `POST`
- **Headers**: `Content-Type: application/json`

## 🧪 Teste

### Testar a API

```bash
curl -X POST http://localhost:5000/api/create-ticket-complete \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste de Ticket",
    "description": "Descrição do problema",
    "category": "INCIDENTE",
    "impact": "MEDIO",
    "location": "Escritório"
  }'
```

### Testar no Copilot Studio

Digite no chat: "Preciso criar um chamado" ou "Abrir ticket"

## 📚 Documentação Adicional

- `COPILOT_HTTP_CONFIG_GUIDE.md` - Guia detalhado de configuração HTTP
- `COPILOT_STUDIO_STEP_BY_STEP.md` - Passo a passo completo
- `COPILOT_IMPORT_INSTRUCTIONS.md` - Instruções de importação
- `GLPI_TROUBLESHOOTING.md` - Solução de problemas do GLPI

## 🔍 Troubleshooting

### API não responde
- Verifique se o Flask está rodando
- Confirme se as variáveis de ambiente estão configuradas
- Teste o endpoint `/api/health`

### Copilot Studio não conecta
- Verifique a URL no tópico
- Confirme se a API está acessível
- Verifique os logs do Flask

### Tickets não são criados no GLPI
- Verifique as credenciais do GLPI
- Confirme se os tokens estão válidos
- Consulte o `GLPI_TROUBLESHOOTING.md`