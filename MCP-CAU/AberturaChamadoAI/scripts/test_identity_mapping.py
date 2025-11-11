import os
import json
import time
from typing import Optional, Dict, Any

import requests


class ScenarioLogger:
    def __init__(self):
        ts = time.strftime("%Y%m%d-%H%M%S")
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        self.path = os.path.join(logs_dir, f"identity_mapping_{ts}.log")

    def _write(self, level: str, msg: str):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"[{level}] {time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")

    def info(self, msg: str):
        self._write("INFO", msg)

    def warn(self, msg: str):
        self._write("WARN", msg)

    def error(self, msg: str):
        self._write("ERROR", msg)


def load_dotenv_local():
    here = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(here, ".env")
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#") or "=" not in s:
                        continue
                    k, v = s.split("=", 1)
                    if k and (k not in os.environ or not os.environ.get(k)):
                        os.environ[k.strip()] = v.strip()
        except Exception:
            pass


def mask_secret(v: Optional[str]) -> str:
    if not v:
        return "<empty>"
    s = str(v)
    return f"***{s[-4:]}" if len(s) > 4 else "***"


class GLPI:
    def __init__(self, logger: ScenarioLogger):
        load_dotenv_local()
        base = os.environ.get("GLPI_BASE_URL", "").strip()
        if not base:
            env_url = os.environ.get("GLPI_URL", "").strip()
            if env_url:
                base = env_url[:-len("/apirest.php")] if env_url.endswith("/apirest.php") else env_url
        if not base:
            raise ValueError("GLPI_BASE_URL/GLPI_URL ausente")
        self.base = base.rstrip("/")
        app_token = os.environ.get("APP_TOKEN", "").strip() or os.environ.get("GLPI_APP_TOKEN", "").strip()
        if not app_token:
            raise ValueError("APP_TOKEN/GLPI_APP_TOKEN ausente")
        self.session = requests.Session()
        self.session.headers.update({"App-Token": app_token})
        self.session_token: Optional[str] = None
        self.logger = logger

    def _log_request(self, method: str, url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None):
        safe_headers = {k: (mask_secret(v) if k.lower() in {"app-token", "session-token", "authorization"} else v)
                        for k, v in headers.items()}
        qp = "" if not params else "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        self.logger.info(f"REQUEST {method} {url}{qp} headers={safe_headers}")

    def _log_response(self, resp: requests.Response):
        details = {"status": resp.status_code, "ok": resp.ok}
        try:
            data = resp.json()
            details["json_keys"] = list(data.keys())
        except Exception:
            details["body_len"] = len(resp.text or "")
        self.logger.info(f"RESPONSE {details}")

    def init_session(self, strategy: str) -> bool:
        url = f"{self.base}/apirest.php/initSession"
        if strategy == "user_token":
            ut = os.environ.get("USER_TOKEN", "").strip() or os.environ.get("GLPI_USER_TOKEN", "").strip()
            if not ut:
                raise ValueError("USER_TOKEN/GLPI_USER_TOKEN ausente")
            headers = {"Authorization": f"user_token {ut}"}
            self._log_request("POST", url, {**self.session.headers, **headers})
            resp = self.session.post(url, headers=headers, timeout=15)
            self._log_response(resp)
            resp.raise_for_status()
            token = resp.json().get("session_token")
            if not token:
                raise RuntimeError("Sem session_token")
            self.session.headers.update({"Session-Token": token})
            self.session_token = token
            return True
        elif strategy == "password":
            username = os.environ.get("GLPI_USERNAME", "").strip()
            password = os.environ.get("GLPI_PASSWORD", "").strip()
            if not username or not password:
                raise ValueError("GLPI_USERNAME/GLPI_PASSWORD ausentes")
            payload = {"login": username, "password": password}
            self._log_request("POST", url, {**self.session.headers, "Content-Type": "application/json"})
            resp = self.session.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            self._log_response(resp)
            resp.raise_for_status()
            token = resp.json().get("session_token")
            if not token:
                raise RuntimeError("Sem session_token")
            self.session.headers.update({"Session-Token": token})
            self.session_token = token
            return True
        else:
            raise ValueError(f"Estratégia não suportada: {strategy}")

    def search_user(self, query: str) -> Dict[str, Any]:
        url = f"{self.base}/apirest.php/search/User"
        params = {
            "criteria[0][field]": "1",  # login/name
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": query,
            "forcedisplay[0]": "2",   # id
            "forcedisplay[1]": "1",   # name
            "forcedisplay[2]": "5",   # email
        }
        self._log_request("GET", url, dict(self.session.headers), params)
        resp = self.session.get(url, params=params, timeout=15)
        self._log_response(resp)
        resp.raise_for_status()
        return resp.json()

    def kill_session(self):
        if not self.session_token:
            return
        url = f"{self.base}/apirest.php/killSession"
        self._log_request("POST", url, dict(self.session.headers))
        resp = self.session.post(url, timeout=10)
        self._log_response(resp)


def main():
    logger = ScenarioLogger()
    strategy = os.environ.get("AUTH_STRATEGY", "user_token")
    m365_upn = os.environ.get("M365_UPN", "").strip() or os.environ.get("GLPI_USERNAME", "").strip()
    if not m365_upn:
        print(json.dumps({"error": "Defina M365_UPN ou GLPI_USERNAME"}))
        return
    client = GLPI(logger)
    try:
        client.init_session(strategy)
        data = client.search_user(m365_upn)
        rows = data.get("data") or []
        matches = []
        for row in rows:
            try:
                matches.append({
                    "id": int(row.get("2")),
                    "name": row.get("1"),
                    "email": row.get("5"),
                })
            except Exception:
                continue
        print(json.dumps({
            "query": m365_upn,
            "matches": matches,
            "count": len(matches)
        }, ensure_ascii=False))
    finally:
        try:
            client.kill_session()
        except Exception:
            pass


if __name__ == "__main__":
    main()