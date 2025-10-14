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


def list_formcreator_forms(api_url: str, session_headers: dict, limit: int = 1000) -> list:
    """Tenta listar formulários via endpoint direto; cai para search se necessário.

    Retorna uma lista normalizada com chaves: id, name, helpdesk_name, is_active.
    """
    params = {"range": f"0-{limit}"}
    url_direct = f"{api_url}/PluginFormcreatorForm"
    resp = requests.get(url_direct, headers=session_headers, params=params, timeout=(5, 15))
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            normalized = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                normalized.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "helpdesk_name": item.get("helpdesk_name"),
                    "is_active": item.get("is_active"),
                })
            return normalized
    # fallback para search com forcedisplay
    params = {
        "range": f"0-{limit}",
        "forcedisplay[0]": "id",
        "forcedisplay[1]": "name",
        "forcedisplay[2]": "is_active",
        "forcedisplay[3]": "helpdesk_name",
    }
    url_search = f"{api_url}/search/PluginFormcreatorForm"
    sresp = requests.get(url_search, headers=session_headers, params=params, timeout=(5, 15))
    sresp.raise_for_status()
    js = sresp.json()
    # tentar mapear cols -> indices
    if isinstance(js, dict) and "data" in js and "cols" in js:
        cols = js["cols"]
        # construir indice->campo
        idx_to_field = {}
        for col in cols:
            idx = str(col.get("index")) if isinstance(col.get("index"), (int, str)) else None
            field = col.get("field")
            if idx and field:
                idx_to_field[idx] = field
        normalized = []
        for row in js["data"]:
            if not isinstance(row, dict):
                continue
            item = {}
            for k, v in row.items():
                field = idx_to_field.get(str(k))
                if field:
                    item[field] = v
            if item:
                normalized.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "helpdesk_name": item.get("helpdesk_name"),
                    "is_active": item.get("is_active"),
                })
        return normalized
    # fim: retorna data crua
    return js.get("data", []) if isinstance(js, dict) else js


def main():
    base = Path(__file__).resolve().parent.parent
    load_env(base / ".env")

    api_url = os.getenv("API_URL")
    app_token = os.getenv("APP_TOKEN")
    user_token = os.getenv("USER_TOKEN")
    if not all([api_url, app_token, user_token]):
        raise SystemExit("Defina API_URL, APP_TOKEN e USER_TOKEN em MCP-CAU/.env")

    headers = authenticate(api_url, app_token, user_token)
    forms = list_formcreator_forms(api_url, headers, limit=2000)

    out_dir = base / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "formcreator_forms.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(forms, f, ensure_ascii=False, indent=2)
    print(f"Gravado: {out_path}")


if __name__ == "__main__":
    main()