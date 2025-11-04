# 🤖 Agente Copilot Studio - Criação de Tickets GLPI

## 📋 Descrição

Sistema integrado entre Microsoft Copilot Studio e GLPI para criação automatizada de tickets de suporte técnico através de conversas naturais. Versão 2.0 com melhorias de robustez e tratamento de erros.

## ✨ Funcionalidades

- 🎫 **Criação de Tickets**: Cria tickets no GLPI via API REST
- 🗣️ **Interface Natural**: Conversa em linguagem natural com o usuário
- ⚡ **API Robusta**: Flask com validações e tratamento de erros
- 🔧 **Fácil Configuração**: Setup rápido com variáveis de ambiente
- 🛡️ **Validações Avançadas**: Detecta expressões PowerFx não processadas
- 📊 **Health Check**: Endpoint para monitoramento do sistema
- 📝 **Logging Estruturado**: Logs detalhados para debugging
- 🎯 **Mapeamento de Categorias**: Interface user-friendly para categorias GLPI

## 🚀 Guia Rápido (Essencial)

### 1) Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas configurações do GLPI
GLPI_URL=http://seu-glpi.com/apirest.php
GLPI_APP_TOKEN=seu_app_token_aqui
GLPI_USER_TOKEN=seu_user_token_aqui
```

### 2) Instalar e Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar API (modo simples)
python app.py

# Alternativa (modo recomendado)
python -m scripts.run_server
```

### 3) Integração com Copilot (opcional)

- Este repositório não inclui um agente Copilot; a API está pronta para consumo por qualquer cliente HTTP.
- Se integrar com Copilot, use a URL `http://localhost:5000/api/create-ticket-complete`, método `POST`, e `Content-Type: application/json`.

## 🔒 Túnel HTTPS (Copilot)

- Por padrão, o Copilot exige `https://`. Para acessar a API local, inicie um túnel HTTPS e use o YAML de túnel.
- Opções comuns:
  - `cloudflared`: `cloudflared tunnel --url http://localhost:5000` → copie `https://<subdominio>.trycloudflare.com`
  - `ngrok`: `ngrok config add-authtoken <SEU_TOKEN>` e `ngrok http 5000` → copie `https://<subdominio>.ngrok.io`

- Importar no Copilot Studio o arquivo `copilot-create-ticket-config.tunnel.yaml` e substituir `https://REPLACE_WITH_TUNNEL` pelo URL gerado do túnel.
- Headers: `Content-Type: application/json`. Corpo: conforme exemplo de payload abaixo.
- Evite usar `http://localhost` no Copilot; use sempre o URL público `https://` do túnel.

## 📁 Estrutura do Projeto

```
MCP-CAU/
├── app.py                              # API Flask principal
├── copilot-create-ticket-config.tunnel.yaml   # Configuração Copilot via túnel HTTPS
├── copilot-create-ticket-product.yaml         # Tópico completo (produção) para criação de tickets
├── copilot-get-user-email.yaml                # Tópico para capturar/validar e-mail do usuário
├── requirements.txt                     # Dependências Python
├── .env.example                        # Exemplo de configuração
├── .gitignore                          # Ignora logs e artefatos locais
├── README.md                           # Este arquivo
└── docs/                               # Documentação
    ├── SETUP_GUIDE.md                  # Guia de configuração completo
    ├── COPILOT_HTTP_CONFIG_GUIDE.md    # Configuração HTTP detalhada
    # (Os guias acima cobrem o essencial; arquivos adicionais podem não existir)
    └── GLPI_TROUBLESHOOTING.md         # Solução de problemas GLPI
```

## 🔌 Endpoints da API

### `GET /api/health`
Verifica se a API e conexão com GLPI estão funcionando.

### `POST /api/create-ticket-complete`
Cria um ticket completo no GLPI.

**Payload:**
```json
{
  "title": "Título do ticket",
  "description": "Descrição do problema",
  "category": "SEGURANCA",
  "impact": "MEDIO",
  "location": "Local do problema",
  "contact_phone": "51999999999",
  "requester_email": "usuario@empresa.com" // opcional: define requerente do ticket
}
```

Observação: o tópico `copilot-create-ticket-product.yaml` coleta o e‑mail do usuário logo no início e envia `requester_email` automaticamente para vincular o requerente no GLPI.

### `GET /api/glpi-user-by-email`
Busca usuário no GLPI pelo e‑mail.

**Uso:**
```bash
curl "http://localhost:5000/api/glpi-user-by-email?email=usuario@empresa.com"
```

**Resposta:**
```json
{
  "sucesso": true,
  "query_email": "usuario@empresa.com",
  "resultado": {
    "found": true,
    "user_id": 123,
    "name": "Usuário Exemplo",
    "login": "u.exemplo",
    "email": "usuario@empresa.com"
  }
}
```

## 🧪 Teste Rápido

```bash
curl -X POST http://localhost:5000/api/create-ticket-complete \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste",
    "description": "Descrição clara com mais de cinquenta caracteres para validação.",
    "category": "SEGURANCA",
    "impact": "MEDIO",
    "location": "Escritório",
    "contact_phone": "51999999999"
  }'
```

## ℹ️ Observações
- Logs não são versionados (`.gitignore` inclui `*.log`).
- Scripts de inicialização legados foram removidos; use `python app.py` ou `python -m scripts.run_server`.

## 🔍 Troubleshooting

- **API não responde**: Verifique se o Flask está rodando e as variáveis de ambiente estão configuradas
- **Copilot Studio não conecta**: Confirme a URL e se a API está acessível
- **Tickets não são criados**: Verifique credenciais do GLPI no arquivo `.env`

Para problemas específicos, consulte a documentação em `docs/`.

## 🛠️ Tecnologias

- **Python 3.x**
- **Flask** - API web minimalista
- **Requests** - Cliente HTTP para GLPI
- **Microsoft Copilot Studio** - Interface conversacional

## 📚 Documentação

Consulte a pasta `docs/` para guias detalhados:
- `SETUP_GUIDE.md` - Configuração completa
- `GLPI_TROUBLESHOOTING.md` - Solução de problemas
- Outros guias específicos do Copilot Studio

## 📄 Licença

Este projeto é de uso interno e educacional.
