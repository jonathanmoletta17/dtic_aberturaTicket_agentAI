import os
import json
from pathlib import Path


def load_forms_db(dir_path: str):
    data = []
    p = Path(dir_path)
    if not p.exists():
        return data
    for f in p.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fh:
            try:
                data.append(json.load(fh))
            except Exception:
                pass
    return data


def format_fields_section(form_data: dict) -> str:
    lines = []
    lines.append("\n\n## Campos do Formulário (extraídos do dump SQL)\n")
    # por seção
    sections = form_data.get("sections", [])
    for sec in sections:
        lines.append(f"- Seção: {sec.get('name')} (ordem: {sec.get('order')})")
        for q in sec.get("questions", []):
            ft = q.get("fieldtype")
            req = q.get("required")
            lines.append(f"  - {q.get('name')} — tipo: `{ft}`, obrigatório: `{req}`")
    return "\n".join(lines)


def update_readme(base_dir: str, form_data: dict):
    slug = form_data["form"]["slug"]
    readme_path = Path(base_dir) / slug / "README.md"
    if not readme_path.exists():
        return False
    with open(readme_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    # remove nota antiga de indisponibilidade se existir
    content = content.replace("Nota: campos do formulário não são expostos via REST API.", "")
    content = content.replace("Observação: os campos/perguntas não estão disponíveis via REST.", "")
    # append seção de campos
    content = content.rstrip() + format_fields_section(form_data)
    with open(readme_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Atualizado: {readme_path}")
    return True


def main():
    forms_db_dir = os.getenv("FORMS_DB_DIR", str(Path("MCP-CAU/output/forms_db").resolve()))
    docs_base = os.getenv("DOCS_BASE_DIR", str(Path("MCP-CAU/forms").resolve()))
    # construir mapping id->slug a partir dos arquivos existentes em MCP-CAU/output/forms
    existing_forms_dir = Path("MCP-CAU/output/forms").resolve()
    id_to_slug = {}
    if existing_forms_dir.exists():
        for f in existing_forms_dir.glob("*_*.json"):
            name = f.name
            try:
                fid_str, slug_part = name.split("_", 1)
                fid = int(fid_str)
                slug_part = slug_part.replace(".json", "")
                id_to_slug[fid] = slug_part
            except Exception:
                pass
    data = load_forms_db(forms_db_dir)
    updated = 0
    for form_data in data:
        # tentar substituir slug pelo já utilizado anteriormente, baseado no id
        fid = form_data.get("form", {}).get("id")
        if fid in id_to_slug:
            form_data["form"]["slug"] = id_to_slug[fid]
        if update_readme(docs_base, form_data):
            updated += 1
    print(f"READMEs atualizados: {updated}")


if __name__ == "__main__":
    main()