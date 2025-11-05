Objetivo
- Configurar e executar dois servidores: API (Flask) e túnel (`ngrok`).

Pré-requisitos
- Windows com PowerShell.
- Python 3.10+ instalado (`python --version`).
- Git instalado (`git --version`).
- Conta/cliente ngrok instalado e autenticado (`ngrok config add-authtoken <SEU_TOKEN>`).

Configurar ambiente (uma vez)
- Criar e ativar ambiente virtual:
  - `python -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
- Instalar dependências:
  - `pip install -r requirements.txt`

Executar servidores (em dois terminais separados)
- Terminal 1: API Flask
  - `.\.venv\Scripts\Activate.ps1`
  - `python -m scripts.run_server`
  - Verificar saúde: `curl.exe http://localhost:5000/api/health`

- Terminal 2: ngrok
  - `ngrok http 5000`
  - Copiar a URL gerada (ex.: `https://XXXX.ngrok-free.app`).

Atualizar URLs nos YAMLs (se a URL do ngrok mudar)
- Substituir a URL nos arquivos:
  - `copilot-create-ticket-product.yaml`
  - `copilot-get-user-email.yaml`
  - `copilot-create-ticket-config.tunnel.yaml`
- Campos a atualizar:
  - `https://<SEU_SUBDOMINIO>.ngrok-free.app/api/glpi-user-by-email?email=`
  - `https://<SEU_SUBDOMINIO>.ngrok-free.app/api/create-ticket-complete`

Testes rápidos
- Health local:
  - `curl.exe http://localhost:5000/api/health`
- Health público (via ngrok):
  - `curl.exe https://<SEU_SUBDOMINIO>.ngrok-free.app/api/health`

Observações
- Sempre executar API e ngrok em terminais separados.
- Em Copilot Studio, importe os YAMLs após qualquer troca de URL do ngrok.