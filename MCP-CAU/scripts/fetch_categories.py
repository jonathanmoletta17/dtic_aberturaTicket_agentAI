import os
import json
import requests
from pathlib import Path


def load_env(env_path: Path) -> None:
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def authenticate(api_url: str, app_token: str, user_token: str) -> dict:
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json",
    }
    resp = requests.post(f"{api_url}/initSession", headers=headers, timeout=(5, 10))
    resp.raise_for_status()
    data = resp.json()
    session_token = data.get("session_token")
    if not session_token:
        raise RuntimeError("GLPI: session_token ausente na resposta de initSession")
    return {"App-Token": app_token, "Session-Token": session_token}


def list_itil_categories(api_url: str, session_headers: dict, limit: int = 1000) -> list:
    """Coleta categorias ITIL com campos nomeados via /ITILCategory.

    Retorna uma lista de objetos com chaves padronizadas (id, name, completename,
    entities_id, comment, is_helpdesk_visible) quando disponíveis.
    """
    params = {"range": f"0-{limit}"}
    url = f"{api_url}/ITILCategory"
    resp = requests.get(url, headers=session_headers, params=params, timeout=(5, 15))
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        normalized = []
        for item in data:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "completename": item.get("completename"),
                "entities_id": item.get("entities_id"),
                "comment": item.get("comment"),
                "is_helpdesk_visible": item.get("is_helpdesk_visible"),
                "itil_categories_id": item.get("id"),
            })
        return normalized
    # fallback ao formato bruto
    return data if data else []


def main():
    base = Path(__file__).resolve().parent.parent
    load_env(base / ".env")

    api_url = os.getenv("API_URL")
    app_token = os.getenv("APP_TOKEN")
    user_token = os.getenv("USER_TOKEN")
    if not all([api_url, app_token, user_token]):
        raise SystemExit("Defina API_URL, APP_TOKEN e USER_TOKEN em MCP-CAU/.env")

    headers = authenticate(api_url, app_token, user_token)
    cats = list_itil_categories(api_url, headers, limit=2000)

    out_dir = base / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "itil_categories.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(cats, f, ensure_ascii=False, indent=2)
    print(f"Gravado: {out_path}")


if __name__ == "__main__":
    main()