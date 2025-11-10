import json
import os
import sys
import requests


def main():
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
    if base_url.endswith("/"):
        base_url = base_url.rstrip("/")
    url = f"{base_url}/api/create-ticket-complete"
    requester_email_env = os.environ.get("REQUESTER_EMAIL")
    payload = {
        "title": "Teste Copilot Studio",
        "description": (
            "Impressora do setor financeiro nao imprime documentos PDF desde ontem. "
            "Ja reiniciei o equipamento, verifiquei cabos e atualizei drivers sem sucesso. "
            "Preciso de suporte para restaurar a impressao."
        ),
        "category": "SOFTWARE",
        "impact": "MEDIO",
        "location": "Escritorio 3A",
        "contact_phone": "11999998888",
        "requester_email": requester_email_env or "usuario@empresa.com",
    }

    try:
        resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        print("Status:", resp.status_code)
        try:
            print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception:
            print(resp.text)
    except Exception as e:
        print("Erro ao enviar requisição:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()