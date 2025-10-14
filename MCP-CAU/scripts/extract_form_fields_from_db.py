import os
import json
from pathlib import Path

import mysql.connector
from mysql.connector import Error


def load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    return {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": int(os.getenv("DB_PORT", "3306")),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME", "glpi"),
        "OUTPUT_DIR": os.getenv("OUTPUT_DIR", str(Path("MCP-CAU/output/forms_db").resolve())),
    }


def slugify(value: str) -> str:
    if not value:
        return ""
    import re
    s = value.strip().upper()
    s = re.sub(r"[ÁÀÂÃ]", "A", s)
    s = re.sub(r"[ÉÈÊ]", "E", s)
    s = re.sub(r"[ÍÌÎ]", "I", s)
    s = re.sub(r"[ÓÒÔÕ]", "O", s)
    s = re.sub(r"[ÚÙÛ]", "U", s)
    s = re.sub(r"Ç", "C", s)
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    return s


def fetch_form_fields(conn):
    sql = (
        "SELECT f.id AS form_id, f.name AS form_name, f.is_active AS form_active, "
        "s.id AS section_id, s.name AS section_name, s.`order` AS section_order, "
        "q.id AS question_id, q.name AS question_name, q.fieldtype AS fieldtype, q.required AS required, "
        "q.default_values AS default_values, q.`order` AS question_order "
        "FROM glpi_plugin_formcreator_forms f "
        "JOIN glpi_plugin_formcreator_sections s ON s.plugin_formcreator_forms_id = f.id "
        "JOIN glpi_plugin_formcreator_questions q ON q.plugin_formcreator_sections_id = s.id "
        "WHERE f.is_deleted = 0 "
        "ORDER BY f.id, s.`order`, q.`order`"
    )
    cur = conn.cursor(dictionary=True)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return rows


def group_by_form(rows):
    forms = {}
    for r in rows:
        fid = r["form_id"]
        if fid not in forms:
            forms[fid] = {
                "form": {
                    "id": fid,
                    "name": r["form_name"],
                    "is_active": r.get("form_active", 1),
                    "slug": slugify(r["form_name"]),
                },
                "sections": {},
                "questions": [],
            }
        # sections
        sid = r["section_id"]
        if sid not in forms[fid]["sections"]:
            forms[fid]["sections"][sid] = {
                "id": sid,
                "name": r["section_name"],
                "order": r.get("section_order"),
                "questions": [],
            }
        q = {
            "id": r["question_id"],
            "name": r["question_name"],
            "fieldtype": r["fieldtype"],
            "required": r["required"],
            "default_values": r.get("default_values"),
            "section_id": sid,
            "order": r.get("question_order"),
        }
        forms[fid]["sections"][sid]["questions"].append(q)
        forms[fid]["questions"].append(q)
    return forms


def save_forms(forms, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for fid, data in forms.items():
        slug = data["form"]["slug"]
        filename = f"{fid}_{slug}.json"
        path = Path(output_dir) / filename
        # transformar sections dict em lista ordenada
        sections_list = sorted(list(data["sections"].values()), key=lambda s: (s.get("order") or 0, s["name"]))
        out = {
            "form": data["form"],
            "sections": sections_list,
            "questions": sorted(data["questions"], key=lambda q: (q.get("order") or 0, q["name"]))
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"Gravado: {path}")


def main():
    env = load_env()
    if not env["DB_USER"] or not env["DB_PASSWORD"]:
        raise RuntimeError("Configure DB_USER e DB_PASSWORD no .env para conectar ao banco GLPI.")
    try:
        conn = mysql.connector.connect(
            host=env["DB_HOST"],
            port=env["DB_PORT"],
            user=env["DB_USER"],
            password=env["DB_PASSWORD"],
            database=env["DB_NAME"],
        )
        rows = fetch_form_fields(conn)
        forms = group_by_form(rows)
        save_forms(forms, env["OUTPUT_DIR"])
    except Error as e:
        raise RuntimeError(f"Erro ao conectar/consultar MySQL: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()