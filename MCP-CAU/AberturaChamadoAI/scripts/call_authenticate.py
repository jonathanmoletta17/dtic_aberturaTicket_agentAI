import json
import os
import argparse
import requests

def main():
    parser = argparse.ArgumentParser(description="Chama /api/authenticate-user de forma segura")
    parser.add_argument("--url", default=os.environ.get("AUTH_URL", "http://127.0.0.1:5000/api/authenticate-user"))
    parser.add_argument("--login", default=os.environ.get("AUTH_LOGIN", ""))
    parser.add_argument("--email", default=os.environ.get("AUTH_EMAIL", ""))
    parser.add_argument("--password", default=os.environ.get("AUTH_PASSWORD", ""))
    parser.add_argument("--totp_code", default=os.environ.get("AUTH_TOTP_CODE", ""))
    args = parser.parse_args()

    url = args.url
    body = {
        'login': args.login,
        'email': args.email,
        'password': args.password,
    }
    if args.totp_code:
        body['totp_code'] = args.totp_code

    if not body['password'] or (not body['login'] and not body['email']):
        print("Parâmetros obrigatórios ausentes: informe --login ou --email e --password (ou via variáveis de ambiente AUTH_LOGIN/AUTH_EMAIL/AUTH_PASSWORD)")
        return

    headers = {'Accept':'application/json','Content-Type':'application/json'}
    r = requests.post(url, json=body, headers=headers, timeout=20)
    print(r.status_code)
    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(r.text)

if __name__ == '__main__':
    main()