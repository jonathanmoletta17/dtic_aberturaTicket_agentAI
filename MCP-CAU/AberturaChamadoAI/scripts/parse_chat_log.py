import re
import json
from pathlib import Path


LOG_PATHS = [
    Path(__file__).resolve().parent.parent / "CuidAI" / "chat_copilot_testes.txt",
    Path("CuidAI/chat_copilot_testes.txt").resolve(),
]


def find_log_path():
    for p in LOG_PATHS:
        if p.exists():
            return p
    raise FileNotFoundError("Não encontrei CuidAI/chat_copilot_testes.txt. Verifique o caminho.")


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_chat_log(text: str):
    lines = text.splitlines()

    events = []
    current = None

    def start_new_event():
        return {
            "time": None,
            "user_query": None,
            "bot_messages": [],
            "target_doc": None,
            "pdf_citations": [],
            "answer_not_found": False,
            "unknown_intent": False,
        }

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Timestamp marker
        if line.startswith("Enviado às"):
            # Start a new event if none
            if current is None or current.get("user_query") or current.get("bot_messages"):
                if current:
                    events.append(current)
                current = start_new_event()
            current["time"] = normalize_text(line)
            i += 1
            continue

        # User said
        if line.startswith("Você disse:"):
            # Capture next lines until blank or next marker
            # Prefer the last non-empty content after the colon
            # Patterns in log can repeat the same message twice
            content = None
            # If there is inline content after colon
            m = re.match(r"Você disse:\s*(.*)", line)
            if m and m.group(1):
                content = normalize_text(m.group(1))
            # Look ahead for the next non-empty line if content is empty
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt:
                    j += 1
                    continue
                if nxt.startswith("Você disse:") or nxt.startswith("O bot disse:") or nxt.startswith("Enviado às"):
                    break
                content = normalize_text(nxt)
                break
            if current is None:
                current = start_new_event()
            current["user_query"] = content
            i += 1
            continue

        # Bot said
        if line.startswith("O bot disse:"):
            # Collect subsequent text lines as one message block
            msg_lines = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip().startswith("Você disse:") or nxt.strip().startswith("O bot disse:") or nxt.strip().startswith("Enviado às"):
                    break
                msg_lines.append(nxt.rstrip("\n"))
                j += 1
            msg = normalize_text("\n".join(msg_lines)) if msg_lines else ""
            if current is None:
                current = start_new_event()
            current["bot_messages"].append(msg)

            # Extract target doc if present
            m_doc = re.search(r"Documento foco:\s*(PGRS|PGRCC|PGRSS)", msg, re.IGNORECASE)
            if m_doc:
                current["target_doc"] = m_doc.group(1).upper()

            # Detect Answer not Found / unknown intent fallback
            if re.search(r"Answer not Found|Não sei como ajudar", msg, re.IGNORECASE):
                current["answer_not_found"] = True
                current["unknown_intent"] = True

            # Extract PDF citation names
            pdfs = re.findall(r"(PGRS_.*?\.pdf|PGRSS_.*?\.pdf|PGRSCC_.*?\.pdf)", msg)
            for pdf in pdfs:
                if pdf not in current["pdf_citations"]:
                    current["pdf_citations"].append(pdf)

            i = j
            continue

        i += 1

    # Append last event if exists
    if current and (current.get("user_query") or current.get("bot_messages")):
        events.append(current)

    return events


def summarize(events):
    summary = {
        "total_events": len(events),
        "answer_not_found_count": sum(1 for e in events if e.get("answer_not_found")),
        "by_target_doc": {
            "PGRS": sum(1 for e in events if e.get("target_doc") == "PGRS"),
            "PGRCC": sum(1 for e in events if e.get("target_doc") == "PGRCC"),
            "PGRSS": sum(1 for e in events if e.get("target_doc") == "PGRSS"),
            "UNKNOWN": sum(1 for e in events if not e.get("target_doc")),
        },
        "anomalies": [],
    }

    for idx, e in enumerate(events):
        anomalies = []
        if not e.get("user_query"):
            anomalies.append("missing_user_query")
        if e.get("answer_not_found"):
            anomalies.append("answer_not_found")
        # Multiple PDFs cited in one answer
        if len(e.get("pdf_citations", [])) > 1:
            anomalies.append("multiple_pdf_citations")
        # No target doc but citations exist
        if not e.get("target_doc") and e.get("pdf_citations"):
            anomalies.append("citations_without_target_doc")
        if anomalies:
            summary["anomalies"].append({"index": idx, "user_query": e.get("user_query"), "issues": anomalies})

    return summary


def main():
    log_path = find_log_path()
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    events = parse_chat_log(text)
    summary = summarize(events)

    print("=== Resumo dos testes ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n=== Eventos detalhados ===")
    for i, e in enumerate(events):
        print(f"\n# Evento {i+1}")
        print(f"Tempo: {e.get('time')}")
        print(f"Pergunta: {e.get('user_query')}")
        print(f"Documento foco: {e.get('target_doc') or 'N/A'}")
        print(f"Citações: {', '.join(e.get('pdf_citations', [])) or 'N/A'}")
        print(f"Answer not Found: {e.get('answer_not_found')}")
        print("Resposta do bot (compacta):")
        # Mostrar apenas primeira linha de cada mensagem para facilitar leitura
        for bm in e.get("bot_messages", [])[:3]:
            first_line = bm.split("\n")[0]
            print(f"- {normalize_text(first_line)[:300]}")


if __name__ == "__main__":
    main()