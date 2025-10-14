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


def list_forms(api_url: str, session_headers: dict, limit: int = 1000) -> list:
    params = {"range": f"0-{limit}"}
    url = f"{api_url}/PluginFormcreatorForm"
    resp = requests.get(url, headers=session_headers, params=params, timeout=(5, 15))
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else []


def get_form_detail(api_url: str, session_headers: dict, form_id: int) -> dict:
    url = f"{api_url}/PluginFormcreatorForm/{form_id}"
    resp = requests.get(url, headers=session_headers, timeout=(5, 15))
    if resp.status_code != 200:
        return {}
    data = resp.json()
    return data if isinstance(data, dict) else {}


def search_questions(api_url: str, session_headers: dict, form_id: int, limit: int = 1000) -> list:
    # tenta diferentes nomes de campo de relacionamento
    candidate_fields = [
        "plugin_formcreator_forms_id",
        "form_id",
        "forms_id",
    ]
    forcedisplay = {
        "forcedisplay[0]": "id",
        "forcedisplay[1]": "name",
        "forcedisplay[2]": "fieldtype",
        "forcedisplay[3]": "required",
        "forcedisplay[4]": "default_values",
        "forcedisplay[5]": "helpdesk_name",
        "forcedisplay[6]": "uuid",
        "forcedisplay[7]": "rank",
    }
    for field in candidate_fields:
        params = {"range": f"0-{limit}", **forcedisplay}
        params.update({
            "criteria[0][field]": field,
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(form_id),
        })
        url = f"{api_url}/search/PluginFormcreatorQuestion"
        resp = requests.get(url, headers=session_headers, params=params, timeout=(5, 20))
        if resp.status_code != 200:
            continue
        js = resp.json()
        # mapear cols -> indices
        if isinstance(js, dict) and "data" in js and "cols" in js:
            cols = js["cols"]
            idx_to_field = {}
            for col in cols:
                idx = str(col.get("index")) if isinstance(col.get("index"), (int, str)) else None
                fieldname = col.get("field")
                if idx and fieldname:
                    idx_to_field[idx] = fieldname
            normalized = []
            for row in js["data"]:
                if not isinstance(row, dict):
                    continue
                item = {}
                for k, v in row.items():
                    fieldname = idx_to_field.get(str(k))
                    if fieldname:
                        item[fieldname] = v
                if item:
                    normalized.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "fieldtype": item.get("fieldtype"),
                        "required": item.get("required"),
                        "default_values": item.get("default_values"),
                        "helpdesk_name": item.get("helpdesk_name"),
                        "uuid": item.get("uuid"),
                        "rank": item.get("rank"),
                    })
            if normalized:
                return normalized
        # fallback: retorna data crua
        if isinstance(js, dict) and js.get("data"):
            return js.get("data")
    return []


def try_list_questions_direct(api_url: str, session_headers: dict, limit: int = 2000) -> list:
    """Tenta listar todas as perguntas diretamente via endpoint do plugin.

    Retorna lista de objetos crus se disponível.
    """
    url = f"{api_url}/PluginFormcreatorQuestion"
    resp = requests.get(url, headers=session_headers, params={"range": f"0-{limit}"}, timeout=(5, 20))
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data if isinstance(data, list) else []


def search_questions_by_itemtypes(api_url: str, session_headers: dict, form_id: int, limit: int = 1000) -> list:
    """Tenta múltiplos itemtypes comuns do Formcreator para coletar perguntas/campos.

    Normaliza resposta para chaves: id, name, fieldtype, required, default_values, section_id, form_id.
    """
    itemtype_candidates = [
        "PluginFormcreatorQuestion",
        "PluginFormcreatorField",
        "PluginFormcreatorForm_Field",
    ]
    normalized_all = []
    for itemtype in itemtype_candidates:
        params = {
            "range": f"0-{limit}",
            "forcedisplay[0]": "id",
            "forcedisplay[1]": "name",
            "forcedisplay[2]": "fieldtype",
            "forcedisplay[3]": "required",
            "forcedisplay[4]": "default_values",
            "forcedisplay[5]": "plugin_formcreator_sections_id",
            "forcedisplay[6]": "plugin_formcreator_forms_id",
        }
        # critério por form_id nas variações de campo
        for field in ("plugin_formcreator_forms_id", "forms_id", "form_id"):
            qparams = dict(params)
            qparams.update({
                "criteria[0][field]": field,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(form_id),
            })
            url = f"{api_url}/search/{itemtype}"
            resp = requests.get(url, headers=session_headers, params=qparams, timeout=(5, 20))
            if resp.status_code != 200:
                continue
            js = resp.json()
            if not (isinstance(js, dict) and "data" in js and "cols" in js):
                continue
            cols = js["cols"]
            idx_to_field = {}
            for col in cols:
                idx = str(col.get("index")) if isinstance(col.get("index"), (int, str)) else None
                fieldname = col.get("field")
                if idx and fieldname:
                    idx_to_field[idx] = fieldname
            for row in js["data"]:
                if not isinstance(row, dict):
                    continue
                item = {}
                for k, v in row.items():
                    fieldname = idx_to_field.get(str(k))
                    if fieldname:
                        item[fieldname] = v
                if item:
                    normalized_all.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "fieldtype": item.get("fieldtype"),
                        "required": item.get("required"),
                        "default_values": item.get("default_values"),
                        "section_id": item.get("plugin_formcreator_sections_id"),
                        "form_id": item.get("plugin_formcreator_forms_id"),
                        "_raw": item,
                    })
            # se já obtivemos dados para um itemtype, não precisa testar outras variações deste itemtype
            if normalized_all:
                break
    return normalized_all


def collect_form_answers(api_url: str, session_headers: dict, form_id: int, sample: int = 50) -> list:
    """Coleta respostas de formulário para inferir campos via itemtypes alternativos.

    Tenta múltiplos itemtypes relacionados a respostas.
    """
    itemtype_candidates = [
        "PluginFormcreatorFormanswer",
        "PluginFormcreatorAnswer",
        "PluginFormcreatorQuestion_Answer",
    ]
    aggregated = []
    for itemtype in itemtype_candidates:
        # 1) tentativa de search com criteria por form_id
        params = {
            "range": f"0-{sample}",
            "forcedisplay[0]": "id",
            "forcedisplay[1]": "name",
            "forcedisplay[2]": "plugin_formcreator_forms_id",
            "forcedisplay[3]": "answers",
            "forcedisplay[4]": "content",
        }
        for field in ("plugin_formcreator_forms_id", "forms_id", "form_id"):
            qparams = dict(params)
            qparams.update({
                "criteria[0][field]": field,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(form_id),
            })
            url = f"{api_url}/search/{itemtype}"
            resp = requests.get(url, headers=session_headers, params=qparams, timeout=(5, 20))
            if resp.status_code == 200:
                js = resp.json()
                if isinstance(js, dict) and "data" in js:
                    aggregated.extend(js.get("data", []))
        # 2) tentativa de listagem direta e filtragem por form id
        url_list = f"{api_url}/{itemtype}"
        resp2 = requests.get(url_list, headers=session_headers, params={"range": f"0-{sample}"}, timeout=(5, 20))
        if resp2.status_code == 200:
            data = resp2.json()
            if isinstance(data, list):
                for r in data:
                    if not isinstance(r, dict):
                        continue
                    if r.get("plugin_formcreator_forms_id") == form_id or r.get("forms_id") == form_id or r.get("form_id") == form_id:
                        aggregated.append(r)
    return aggregated


def slugify_name(name: str) -> str:
    nm = name.upper().strip()
    replacements = {
        "EMAIL E APLICATIVOS OFFICE 365": "EMAIL_APPS_365",
        "IMPRESSORA": "IMPRESSORA",
        "REDE": "REDE",
        "PROA-ACESSO": "PROA_ACESSO",
        "SISTEMAS INTERNOS": "SISTEMAS_INTERNOS",
        "INCIDENTE": "INCIDENTE",
        "REQUISIÇÃO": "REQUISICAO",
        "INFRAESTRUTURA": "INFRAESTRUTURA",
        "NOMEIA / EXONERA": "NOMEIA_EXONERA",
        "TRANFERÊNCIA DE EQUIPAMENTOS": "TRANSFERENCIA_EQUIPAMENTOS",
    }
    return replacements.get(nm, nm.replace(" ", "_").replace("/", "_"))


def main():
    base = Path(__file__).resolve().parent.parent
    load_env(base / ".env")

    api_url = os.getenv("API_URL")
    app_token = os.getenv("APP_TOKEN")
    user_token = os.getenv("USER_TOKEN")
    if not all([api_url, app_token, user_token]):
        raise SystemExit("Defina API_URL, APP_TOKEN e USER_TOKEN em MCP-CAU/.env")

    headers = authenticate(api_url, app_token, user_token)
    forms = list_forms(api_url, headers, limit=2000)

    out_dir = base / "output" / "forms"
    out_dir.mkdir(parents=True, exist_ok=True)
    index_out = base / "output" / "formcreator_forms.json"

    # garantir que temos um index normalizado
    index = []
    for form in forms:
        if not isinstance(form, dict):
            continue
        idx_item = {
            "id": form.get("id"),
            "name": form.get("name"),
            "helpdesk_name": form.get("helpdesk_name"),
            "is_active": form.get("is_active"),
            "slug": slugify_name(form.get("name") or ""),
        }
        index.append(idx_item)
        # coletar perguntas por formulário (tenta search com criteria)
        questions = search_questions(api_url, headers, form_id=form.get("id"))
        if not questions:
            # tenta listar por itemtypes alternativos
            questions = search_questions_by_itemtypes(api_url, headers, form_id=form.get("id"))
        if not questions:
            # tenta listar tudo e filtrar por form id
            allq = try_list_questions_direct(api_url, headers, limit=2000)
            if isinstance(allq, list):
                f_id = form.get("id")
                # tentar várias chaves possíveis de relacionamento
                filtered = [q for q in allq if (
                    (isinstance(q, dict) and (
                        q.get("plugin_formcreator_forms_id") == f_id or
                        q.get("forms_id") == f_id or
                        q.get("form_id") == f_id
                    ))
                )]
                questions = filtered

        # tentativa de inferir campos via respostas (fallback)
        inferred_fields = []
        if not questions:
            answers = collect_form_answers(api_url, headers, form_id=form.get("id"), sample=50)
            # respostas de search têm estrutura com cols/data; tentar decodificar
            for a in answers:
                if isinstance(a, dict) and "answers" in a:
                    # alguns plugins armazenam string JSON em "answers"
                    val = a.get("answers")
                    try:
                        parsed = json.loads(val) if isinstance(val, str) else val
                    except Exception:
                        parsed = None
                    if isinstance(parsed, (list, dict)):
                        # lista de pares ou dict question->value
                        if isinstance(parsed, list):
                            for entry in parsed:
                                label = entry.get("question") or entry.get("name") or entry.get("label")
                                if label and label not in [f.get("name") for f in inferred_fields]:
                                    inferred_fields.append({"name": label, "source": "answers_inferred"})
                        else:
                            for label in parsed.keys():
                                if label and label not in [f.get("name") for f in inferred_fields]:
                                    inferred_fields.append({"name": label, "source": "answers_inferred"})
                # outras variações
                if isinstance(a, dict) and "content" in a and not inferred_fields:
                    # tentar extrair labels de HTML ou texto simples
                    content = a.get("content")
                    if isinstance(content, str):
                        # heurística simples: linhas com ':' como Label: valor
                        for line in content.splitlines():
                            if ":" in line:
                                label = line.split(":", 1)[0].strip()
                                if label and label not in [f.get("name") for f in inferred_fields]:
                                    inferred_fields.append({"name": label, "source": "content_inferred"})
        # se inferiu algo, coloca em questions como mínimo
        if not questions and inferred_fields:
            questions = inferred_fields
        # fallback: obter detalhes do formulário (pode conter 'content' com estrutura)
        detail = get_form_detail(api_url, headers, form.get("id"))
        out_path = out_dir / f"{form.get('id')}_{idx_item['slug']}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump({
                "form": idx_item,
                "questions": questions,
                "detail": detail,
            }, f, ensure_ascii=False, indent=2)

    # atualiza também o index na pasta output
    with index_out.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Gravado detalhes em: {out_dir}")


if __name__ == "__main__":
    main()