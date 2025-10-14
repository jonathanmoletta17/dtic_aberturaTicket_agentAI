import re
import os
import json
from pathlib import Path


TARGET_TABLES = {
    "glpi_plugin_formcreator_forms": {
        "key": "forms",
    },
    "glpi_plugin_formcreator_sections": {
        "key": "sections",
        "fk": "plugin_formcreator_forms_id",
    },
    "glpi_plugin_formcreator_questions": {
        "key": "questions",
        "fk": "plugin_formcreator_sections_id",
    },
}


def slugify(value: str) -> str:
    if not value:
        return ""
    s = value.strip().upper()
    s = re.sub(r"[ÁÀÂÃ]", "A", s)
    s = re.sub(r"[ÉÈÊ]", "E", s)
    s = re.sub(r"[ÍÌÎ]", "I", s)
    s = re.sub(r"[ÓÒÔÕ]", "O", s)
    s = re.sub(r"[ÚÙÛ]", "U", s)
    s = re.sub(r"Ç", "C", s)
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def read_dump(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def find_insert_blocks(sql: str, table: str) -> list:
    # com lista de colunas
    pattern_cols = re.compile(rf"INSERT\s+INTO\s+`?{re.escape(table)}`?\s*\(([^)]+)\)\s*VALUES\s*(.+?);", re.IGNORECASE | re.DOTALL)
    return pattern_cols.findall(sql)


def find_insert_blocks_no_cols(sql: str, table: str) -> list:
    # sem lista de colunas (requer ordem oriunda do CREATE TABLE)
    pattern = re.compile(rf"INSERT\s+INTO\s+`?{re.escape(table)}`?\s*VALUES\s*(.+?);", re.IGNORECASE | re.DOTALL)
    return pattern.findall(sql)


def parse_create_table_columns(sql: str, table: str) -> list:
    # captura bloco CREATE TABLE ... (...);
    m = re.search(rf"CREATE\s+TABLE\s+`?{re.escape(table)}`?\s*\((.+?)\)\s*;", sql, re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    cols = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("PRIMARY KEY") or line.startswith("KEY ") or line.startswith("UNIQUE KEY"):
            continue
        # linha de coluna: `id` int(11) NOT NULL AUTO_INCREMENT,
        cm = re.match(r"`([^`]+)`\s+", line)
        if cm:
            cols.append(cm.group(1))
    return cols


def collect_create_table_columns(sql: str, table: str) -> list:
    # Coleta todas as definições de CREATE TABLE para a tabela alvo, com posição
    pattern = re.compile(rf"CREATE\s+TABLE\s+`?{re.escape(table)}`?\s*\((.+?)\)\s*;", re.IGNORECASE | re.DOTALL)
    schemas = []
    for m in pattern.finditer(sql):
        body = m.group(1)
        cols = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("PRIMARY KEY") or line.startswith("KEY ") or line.startswith("UNIQUE KEY"):
                continue
            cm = re.match(r"`([^`]+)`\s+", line)
            if cm:
                cols.append(cm.group(1))
        schemas.append({"pos": m.start(), "cols": cols})
    return schemas


def split_top_level_groups(values_str: str) -> list:
    groups = []
    buf = []
    depth = 0
    in_str = False
    esc = False
    for ch in values_str:
        buf.append(ch)
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == "'":
                in_str = False
            continue
        else:
            if ch == "'":
                in_str = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    groups.append("".join(buf).strip())
                    buf = []
            elif ch == "," and depth == 0:
                # separador entre grupos múltiplos (raramente aparece fora)
                if buf:
                    # já tratamos quando fecha )
                    pass
    return groups


def split_fields(group: str) -> list:
    assert group.startswith("(") and group.endswith(")")
    inner = group[1:-1]
    fields = []
    buf = []
    in_str = False
    esc = False
    depth = 0
    for ch in inner:
        if in_str:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == "'":
                in_str = False
            continue
        if ch == "'":
            in_str = True
            buf.append(ch)
        elif ch == "," and depth == 0:
            fields.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
            if ch in ("(", ")"):
                # nested funcs not expected; keep depth for safety
                depth += 1 if ch == "(" else -1
    if buf:
        fields.append("".join(buf).strip())
    return fields


def clean_value(val: str):
    if val.upper() == "NULL":
        return None
    # remove outer quotes if present
    if len(val) >= 2 and val[0] == "'" and val[-1] == "'":
        s = val[1:-1]
        # unescape common MySQL dump escapes
        s = s.replace("\\'", "'").replace("''", "'").replace("\\n", "\n").replace("\\r", "\r")
        s = s.replace("\\t", "\t").replace("\\\\", "\\")
        return s
    # numeric
    try:
        if "." in val:
            return float(val)
        return int(val)
    except Exception:
        return val


def parse_insert(sql: str, table: str) -> list:
    rows = []
    # regex robusto para capturar INSERT/REPLACE INTO ... (opcional lista de colunas) VALUES ...;
    stmt_pattern = re.compile(
        rf"(INSERT|REPLACE)\s+INTO\s+(?:`?\w+`?\.)?`?{re.escape(table)}`?\s*(\(([^)]+)\))?\s*VALUES\s*(.+?);",
        re.IGNORECASE | re.DOTALL,
    )
    stmts = list(stmt_pattern.finditer(sql))
    print(f"[DIAG] {table}: matched INSERT statements with VALUES = {len(stmts)}")
    # Pré-coletar esquemas de CREATE TABLE com posição para escolher o mais próximo
    schemas = collect_create_table_columns(sql, table)
    # Função para escolher o esquema mais próximo antes da posição do INSERT
    def nearest_schema(pos: int):
        prev = None
        for sc in schemas:
            if sc["pos"] <= pos:
                if prev is None or sc["pos"] >= prev["pos"]:
                    prev = sc
        # fallback: se não achar anterior, usar o primeiro disponível
        return prev["cols"] if prev else (schemas[0]["cols"] if schemas else [])

    for idx, m in enumerate(stmts):
        cols_inside = m.group(3)
        values_str = m.group(4)
        has_cols = bool(cols_inside)
        print(f"[DIAG] {table} stmt#{idx+1}: has_cols={has_cols}")
        cols = None
        if cols_inside:
            cols = [c.strip().strip("`") for c in cols_inside.split(",")]
        groups = split_top_level_groups(values_str)
        print(f"[DIAG] {table} stmt#{idx+1}: groups={len(groups)}")
        # Seleciona esquema apropriado se não houver lista de colunas
        schema_cols = nearest_schema(m.start()) if not cols_inside else None
        for g in groups:
            gg = g.strip()
            if not (gg.startswith("(") and gg.endswith(")")):
                continue
            fields = split_fields(gg)
            if cols:
                # mapear pelo tamanho mínimo para tolerar colunas extras
                n = min(len(fields), len(cols))
                obj = {cols[i]: clean_value(fields[i]) for i in range(n)}
                if len(fields) != len(cols):
                    print(f"[DIAG] {table} stmt#{idx+1}: len(fields)={len(fields)} != len(cols)={len(cols)} -> mapped {n}")
            else:
                if not schema_cols:
                    # sem esquema, ignorar com aviso
                    print(f"[DIAG] {table} stmt#{idx+1}: no schema cols available; skipping group")
                    continue
                n = min(len(fields), len(schema_cols))
                obj = {schema_cols[i]: clean_value(fields[i]) for i in range(n)}
                if len(fields) != len(schema_cols):
                    print(f"[DIAG] {table} stmt#{idx+1}: len(fields)={len(fields)} != len(schema_cols)={len(schema_cols)} -> mapped {n}")
            rows.append(obj)
    return rows


def build_structure(forms, sections, questions):
    # index by id
    forms_by_id = {f["id"]: f for f in forms}
    sections_by_id = {s["id"]: s for s in sections}
    # attach
    out = {}
    for fid, f in forms_by_id.items():
        out[fid] = {
            "form": {
                "id": f.get("id"),
                "name": f.get("name"),
                "is_active": f.get("is_active"),
                "slug": slugify(f.get("name") or ""),
            },
            "sections": {},
            "questions": [],
        }
    for s in sections:
        fid = s.get("plugin_formcreator_forms_id")
        if fid in out:
            out[fid]["sections"][s["id"]] = {
                "id": s["id"],
                "name": s.get("name"),
                "order": s.get("order"),
                "questions": [],
            }
    for q in questions:
        sid = q.get("plugin_formcreator_sections_id")
        # find fid via section
        section = sections_by_id.get(sid)
        if not section:
            continue
        fid = section.get("plugin_formcreator_forms_id")
        if fid not in out:
            continue
        qobj = {
            "id": q.get("id"),
            "name": q.get("name"),
            "fieldtype": q.get("fieldtype"),
            "required": q.get("required"),
            "default_values": q.get("default_values"),
            "section_id": sid,
            "order": q.get("order"),
        }
        out[fid]["questions"].append(qobj)
        if sid in out[fid]["sections"]:
            out[fid]["sections"][sid]["questions"].append(qobj)
    # sort sections and questions
    for fid, data in out.items():
        # sections dict to list
        data["sections"] = sorted(list(data["sections"].values()), key=lambda s: (s.get("order") or 0, s.get("name") or ""))
        # sort questions
        data["questions"] = sorted(data["questions"], key=lambda q: (q.get("order") or 0, q.get("name") or ""))
        for s in data["sections"]:
            s["questions"] = sorted(s["questions"], key=lambda q: (q.get("order") or 0, q.get("name") or ""))
    return out


def save_outputs(structure: dict, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for fid, data in structure.items():
        slug = data["form"]["slug"]
        path = Path(output_dir) / f"{fid}_{slug}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Gravado: {path}")


def main():
    dump_path = os.getenv("GLPI_SQL_DUMP")
    # fallback to arg 1
    import sys
    if not dump_path and len(sys.argv) > 1:
        dump_path = sys.argv[1]
    if not dump_path:
        raise RuntimeError("Informe o caminho do dump via env GLPI_SQL_DUMP ou argumento.")
    sql = read_dump(dump_path)
    # Diagnóstico: detectar ocorrências de CREATE/INSERT por tabela
    def diag(table: str):
        ct = len(re.findall(rf"CREATE\s+TABLE\s+`?{re.escape(table)}`?", sql, re.IGNORECASE))
        it = len(re.findall(rf"(INSERT|REPLACE)\s+INTO\s+(?:`?\w+`?\.)?`?{re.escape(table)}`?", sql, re.IGNORECASE))
        print(f"[DIAG] {table}: CREATE occurrences={ct}, INSERT occurrences={it}")
    for t in ["glpi_plugin_formcreator_forms", "glpi_plugin_formcreator_sections", "glpi_plugin_formcreator_questions"]:
        diag(t)
    forms = parse_insert(sql, "glpi_plugin_formcreator_forms")
    sections = parse_insert(sql, "glpi_plugin_formcreator_sections")
    questions = parse_insert(sql, "glpi_plugin_formcreator_questions")
    print(f"Forms parsed: {len(forms)} | Sections parsed: {len(sections)} | Questions parsed: {len(questions)}")
    if not forms and not sections and not questions:
        print("Nenhum INSERT dos alvos encontrado; verifique o formato do dump.")
    structure = build_structure(forms, sections, questions)
    output_dir = os.getenv("OUTPUT_DIR", str(Path("MCP-CAU/output/forms_db").resolve()))
    save_outputs(structure, output_dir)


if __name__ == "__main__":
    main()