import os
import time
import json
import uuid
from typing import Optional, Dict, Any

import requests


class ScenarioLogger:
    def __init__(self, strategy: str):
        ts = time.strftime("%Y%m%d-%H%M%S")
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        self.path = os.path.join(logs_dir, f"auth_{strategy}_{ts}.log")

    def _write(self, level: str, msg: str):
        line = f"[{level}] {time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)

    def info(self, msg: str):
        self._write("INFO", msg)

    def warn(self, msg: str):
        self._write("WARN", msg)

    def error(self, msg: str):
        self._write("ERROR", msg)


def mask_secret(value: Optional[str]) -> str:
    if not value:
        return "<empty>"
    v = str(value)
    if len(v) <= 4:
        return "***"
    return f"***{v[-4:]}"


class GLPIClient:
    def __init__(self, logger: ScenarioLogger):
        # Carregar .env local sem expor segredos no log
        self._load_dotenv_local()
        base = os.environ.get("GLPI_BASE_URL", "").strip()
        # Mapear GLPI_URL (padrão do projeto) se GLPI_BASE_URL não definido
        if not base:
            env_url = os.environ.get("GLPI_URL", "").strip()
            if env_url:
                # Se vier com /apirest.php, remover para evitar duplicar
                if env_url.endswith("/apirest.php"):
                    base = env_url[: -len("/apirest.php")]
                else:
                    base = env_url
        if not base:
            raise ValueError("GLPI_BASE_URL ausente em variáveis de ambiente")
        self.base = base.rstrip("/")
        app_token = os.environ.get("APP_TOKEN", "").strip()
        if not app_token:
            app_token = os.environ.get("GLPI_APP_TOKEN", "").strip()
        if not app_token:
            raise ValueError("APP_TOKEN ausente em variáveis de ambiente")
        self.app_token = app_token
        self.session_token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({"App-Token": self.app_token})
        self.logger = logger
        self._last_token_for_verification: Optional[str] = None

    @staticmethod
    def _load_dotenv_local():
        # Tenta carregar AberturaChamadoAI/.env
        here = os.path.dirname(os.path.dirname(__file__))
        env_path = os.path.join(here, ".env")
        if not os.path.isfile(env_path):
            return
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    if "=" not in s:
                        continue
                    k, v = s.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    # Não sobrescrever env já definido
                    if k and (k not in os.environ or not os.environ.get(k)):
                        os.environ[k] = v
        except Exception:
            # Silencioso: ambiente pode não permitir leitura
            pass

    def _log_request(self, method: str, url: str, headers: Dict[str, str], body: Optional[Dict[str, Any]]):
        safe_headers = {k: (mask_secret(v) if k.lower() in {"app-token", "session-token", "authorization"} else v)
                        for k, v in headers.items()}
        body_repr = "{}" if body is None else json.dumps({k: ("<redacted>" if k.lower() in {"password", "user_token", "totp", "code"} else v)
                                                          for k, v in body.items()}, ensure_ascii=False)
        self.logger.info(f"REQUEST {method} {url} headers={safe_headers} body={body_repr}")

    def _log_response(self, resp: requests.Response):
        minimum = {
            "status": resp.status_code,
            "ok": resp.ok,
        }
        try:
            data = resp.json()
            # remove secrets if any accidental echo
            for k in ["session_token"]:
                if k in data and isinstance(data[k], str):
                    data[k] = mask_secret(data[k])
            minimum["json_keys"] = list(data.keys())
        except Exception:
            minimum["body_len"] = len(resp.text or "")
        self.logger.info(f"RESPONSE {minimum}")

    def init_session_user_token(self, user_token: str) -> str:
        url = f"{self.base}/apirest.php/initSession"
        headers = {"Authorization": f"user_token {user_token}"}
        self._log_request("POST", url, {**self.session.headers, **headers}, None)
        resp = self.session.post(url, headers=headers, timeout=20)
        self._log_response(resp)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("session_token")
        if not token:
            raise RuntimeError("Falha ao obter session_token com user_token")
        self.session_token = token
        self.session.headers.update({"Session-Token": token})
        self.logger.info(f"Sessão iniciada (token={mask_secret(token)})")
        return token

    def init_session_login_password(self, username: str, password: str, totp_code: Optional[str] = None) -> str:
        url = f"{self.base}/apirest.php/initSession"
        payload: Dict[str, Any] = {"login": username, "password": password}
        if totp_code:
            # campo do TOTP varia por versão; tentar 'code' e fallback
            payload["code"] = totp_code
        headers = {"Content-Type": "application/json"}
        self._log_request("POST", url, {**self.session.headers, **headers}, payload)
        resp = self.session.post(url, json=payload, headers=headers, timeout=20)
        self._log_response(resp)
        if resp.status_code == 401 and not totp_code:
            raise RuntimeError("Autenticação requer TOTP: definir TOTP_CODE em ambiente e reexecutar")
        resp.raise_for_status()
        data = resp.json()
        token = data.get("session_token")
        if not token:
            raise RuntimeError("Falha ao obter session_token com login/senha")
        self.session_token = token
        self.session.headers.update({"Session-Token": token})
        self.logger.info(f"Sessão iniciada (token={mask_secret(token)})")
        return token

    def kill_session(self):
        if not self.session_token:
            return
        url = f"{self.base}/apirest.php/killSession"
        self._log_request("POST", url, dict(self.session.headers), None)
        resp = self.session.post(url, timeout=15)
        self._log_response(resp)
        resp.raise_for_status()
        self.logger.info("Sessão encerrada com sucesso")
        # Guardar token para verificação pós-logout
        self._last_token_for_verification = self.session_token
        self.session.headers.pop("Session-Token", None)
        self.session_token = None

    def check_session_token_valid(self, token: Optional[str]) -> bool:
        if not token:
            return False
        url = f"{self.base}/apirest.php/getFullSession"
        headers = {**self.session.headers, "Session-Token": token}
        self._log_request("GET", url, headers, None)
        resp = self.session.get(url, headers=headers, timeout=10)
        self._log_response(resp)
        if resp.status_code == 401:
            self.logger.info("Token inválido/expirado conforme esperado")
            return False
        if not resp.ok:
            return False
        try:
            data = resp.json()
            glpi_id = data.get("glpiID")
            # Considera válido apenas se há um glpiID ativo
            return glpi_id is not None
        except Exception:
            return False

    def get_full_session_user_id(self) -> Optional[int]:
        url = f"{self.base}/apirest.php/getFullSession"
        self._log_request("GET", url, dict(self.session.headers), None)
        resp = self.session.get(url, timeout=15)
        self._log_response(resp)
        if resp.ok:
            try:
                data = resp.json()
                sid = data.get("glpiID")
                if isinstance(sid, int):
                    self.logger.info(f"glpiID ativo: {sid}")
                    return sid
            except Exception:
                pass
        self.logger.warn("Não foi possível obter glpiID via getFullSession")
        return None

    def search_user_id_by_login(self, login: str) -> Optional[int]:
        url = f"{self.base}/apirest.php/search/User"
        params = {
            "criteria[0][field]": "1",  # name/login field
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": login,
            "forcedisplay[0]": "2",  # id
            "forcedisplay[1]": "1",  # name
        }
        self._log_request("GET", url + "?" + "&".join([f"{k}={v}" for k, v in params.items()]), dict(self.session.headers), None)
        resp = self.session.get(url, params=params, timeout=15)
        self._log_response(resp)
        if not resp.ok:
            return None
        data = resp.json()
        rows = data.get("data") or []
        for row in rows:
            if str(row.get("1", "")).strip().lower() == login.strip().lower():
                try:
                    return int(row.get("2"))
                except Exception:
                    continue
        return None

    def create_ticket(self, name: str, content: str, itilcategories_id: Optional[int] = None) -> int:
        url = f"{self.base}/apirest.php/Ticket"
        body: Dict[str, Any] = {"name": name, "content": content}
        if itilcategories_id:
            body["itilcategories_id"] = itilcategories_id
        headers = {"Content-Type": "application/json"}
        self._log_request("POST", url, {**self.session.headers, **headers}, body)
        resp = self.session.post(url, json=body, headers=headers, timeout=20)
        self._log_response(resp)
        if not resp.ok:
            # fallback 1: formato com wrapper 'input'
            wrapped = {"input": body}
            self.logger.warn("Tentando criação com wrapper 'input'")
            self._log_request("POST", url, {**self.session.headers, **headers}, wrapped)
            resp = self.session.post(url, json=wrapped, headers=headers, timeout=20)
            self._log_response(resp)
            if not resp.ok:
                # fallback 2: adicionar campos comuns mínimos
                fallback2 = body.copy()
                fallback2.setdefault("type", 1)  # incidente
                fallback2.setdefault("requesttypes_id", 1)  # padrão
                self.logger.warn("Tentando criação com campos mínimos adicionais (type, requesttypes_id)")
                self._log_request("POST", url, {**self.session.headers, **headers}, fallback2)
                resp = self.session.post(url, json=fallback2, headers=headers, timeout=20)
                self._log_response(resp)
                if not resp.ok:
                    # fallback 3: wrapper 'input' + adicionais
                    wrapped2 = {"input": fallback2}
                    self.logger.warn("Tentando criação com wrapper 'input' + campos adicionais")
                    self._log_request("POST", url, {**self.session.headers, **headers}, wrapped2)
                    resp = self.session.post(url, json=wrapped2, headers=headers, timeout=20)
                    self._log_response(resp)
                    resp.raise_for_status()
        data = resp.json()
        tid = data.get("id") or data.get("ticket", {}).get("id")
        if not tid:
            raise RuntimeError("Falha ao obter ID do ticket criado")
        self.logger.info(f"Ticket criado id={tid}")
        return int(tid)

    def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        url = f"{self.base}/apirest.php/Ticket/{ticket_id}"
        self._log_request("GET", url, dict(self.session.headers), None)
        resp = self.session.get(url, timeout=15)
        self._log_response(resp)
        resp.raise_for_status()
        return resp.json()

    def close_ticket(self, ticket_id: int) -> bool:
        url = f"{self.base}/apirest.php/Ticket/{ticket_id}"
        body = {"status": 6}
        headers = {"Content-Type": "application/json"}
        self._log_request("PUT", url, {**self.session.headers, **headers}, body)
        resp = self.session.put(url, json=body, headers=headers, timeout=20)
        self._log_response(resp)
        return resp.ok


def verify_authorship(client: GLPIClient, ticket_id: int, expected_user_id: Optional[int]) -> Dict[str, Any]:
    ticket = client.get_ticket(ticket_id)
    fields = {
        "users_id_recipient": ticket.get("users_id_recipient"),
        "users_id_requester": ticket.get("users_id_requester"),
        "users_id_lastupdater": ticket.get("users_id_lastupdater"),
        "created_by": ticket.get("created_by"),
    }
    result = {
        "ticket_id": ticket_id,
        "authorship_match": False,
        "observed_fields": fields,
    }
    if expected_user_id:
        if expected_user_id in [fields.get("users_id_recipient"), fields.get("users_id_requester"), fields.get("created_by")]:
            result["authorship_match"] = True
    return result


def run_strategy(strategy: str) -> Dict[str, Any]:
    logger = ScenarioLogger(strategy)
    client = GLPIClient(logger)
    session_token = None
    expected_uid: Optional[int] = None
    created_ticket_id: Optional[int] = None

    try:
        if strategy == "user_token":
            user_token = os.environ.get("USER_TOKEN", "").strip()
            if not user_token:
                user_token = os.environ.get("GLPI_USER_TOKEN", "").strip()
            if not user_token:
                raise ValueError("USER_TOKEN ausente para estratégia user_token")
            session_token = client.init_session_user_token(user_token)
            expected_uid = client.get_full_session_user_id()
            if not expected_uid:
                glpi_username = os.environ.get("GLPI_USERNAME", "").strip()
                if glpi_username:
                    expected_uid = client.search_user_id_by_login(glpi_username)

        elif strategy == "password":
            username = os.environ.get("GLPI_USERNAME", "").strip()
            password = os.environ.get("GLPI_PASSWORD", "").strip()
            if not username or not password:
                raise ValueError("GLPI_USERNAME/GLPI_PASSWORD ausentes para estratégia password")
            totp_code = os.environ.get("TOTP_CODE", None)
            session_token = client.init_session_login_password(username, password, totp_code)
            expected_uid = client.get_full_session_user_id()
            if not expected_uid:
                expected_uid = client.search_user_id_by_login(username)

        elif strategy == "cas":
            cas_host = os.environ.get("CAS_HOST", "")
            if not cas_host:
                logger.warn("CAS não configurado; cenário será marcado como skip")
                return {"strategy": strategy, "skipped": True, "reason": "CAS não configurado"}
            logger.warn("Fluxo CAS via API não suportado diretamente; forneça sessão existente via cookie em outra ferramenta e teste manual.")
            return {"strategy": strategy, "skipped": True, "reason": "CAS requer sessão web"}

        elif strategy == "sso_external":
            sso_logout = os.environ.get("SSO_LOGOUT_URL", "")
            if not sso_logout:
                logger.warn("SSO externo não configurado; cenário será marcado como skip")
                return {"strategy": strategy, "skipped": True, "reason": "SSO externo não configurado"}
            logger.warn("Fluxo SSO por variáveis do servidor não é exposto via API; requer sessão web.")
            return {"strategy": strategy, "skipped": True, "reason": "SSO externo requer sessão web"}

        else:
            raise ValueError(f"Estratégia desconhecida: {strategy}")

        title = f"[AUTH-TEST] {strategy} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        tag_text = "auth_test"
        content = f"Teste de autenticação {strategy}. tag={tag_text} run_id={uuid.uuid4()}"
        created_ticket_id = client.create_ticket(name=title, content=content)

        verification = verify_authorship(client, created_ticket_id, expected_uid)
        logger.info(f"Verificação: {verification}")

        cleanup = os.environ.get("CLEANUP", "0").strip() == "1"
        if cleanup and created_ticket_id:
            closed = client.close_ticket(created_ticket_id)
            logger.info(f"Rollback (fechar ticket): {'ok' if closed else 'falhou'}")

        logout_verified = False
        # Verificação será feita no finally
        return {
            "strategy": strategy,
            "session_started": bool(session_token),
            "ticket_id": created_ticket_id,
            "expected_user_id": expected_uid,
            "authorship_match": verification.get("authorship_match", False),
            "observed_fields": verification.get("observed_fields", {}),
            "cleanup": cleanup,
            "logout_verified": logout_verified,
        }

    finally:
        if strategy in {"user_token", "password"}:
            try:
                client.kill_session()
                # Após killSession, tentar validar que o token anterior foi invalidado
                logout_verified = not client.check_session_token_valid(client._last_token_for_verification)
                client.logger.info(f"Logout verificado: {'ok' if logout_verified else 'falhou'}")
            except Exception as e:
                logger.error(f"Erro ao encerrar sessão: {e}")


def main():
    strategy = os.environ.get("AUTH_STRATEGY", "").strip() or "password"
    result = run_strategy(strategy)
    print(json.dumps({
        k: (v if k not in {"observed_fields"} else v)
        for k, v in result.items()
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()