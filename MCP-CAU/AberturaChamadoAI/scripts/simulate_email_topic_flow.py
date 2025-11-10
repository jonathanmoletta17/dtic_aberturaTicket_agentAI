"""
Simulador externo (fora do código de produção) para estudar uma arquitetura
modular de tópicos no Copilot Studio:

- Tópico 1: Validação de e-mail com retentativa e lookup GLPI
- Tópico 2: Preenchimento de slots (título, descrição, categoria, impacto,
            localização, telefone) – aqui apenas emulamos o estado
- Tópico 3: Criação do ticket – só permite POST quando todos os campos
            obrigatórios estão válidos

Objetivo: validar ideias de controle de fluxo (gating) e UX de retentativa
sem alterar o código de produção.

Execução:
    python -m AberturaChamadoAI.scripts.simulate_email_topic_flow

Observação: este script NÃO chama serviços externos reais; usa stubs para
emular o lookup de usuário no GLPI e o POST de criação de ticket.
"""

from dataclasses import dataclass, field
import re
from typing import Optional, Dict, Any


# -----------------------------
# Utilidades de validação
# -----------------------------
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))


def sanitize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")


def is_valid_phone(phone: str) -> bool:
    return len(sanitize_phone(phone)) >= 8


def normalize_category(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    txt = raw.strip().upper()
    mapping = {
        "IMPRESSORA": "HARDWARE_IMPRESSORA",
        "COMPUTADOR": "HARDWARE_COMPUTADOR",
        "MONITOR": "HARDWARE_MONITOR",
        "SOFTWARE": "SOFTWARE",
        "REDE": "CONECTIVIDADE",
        "CONECTIVIDADE": "CONECTIVIDADE",
        "SEGURANCA": "SEGURANCA",
        "SEGURANÇA": "SEGURANCA",
        "SOLICITACAO": "SOLICITACAO",
        "SOLICITAÇÃO": "SOLICITACAO",
        "OUTROS": "OUTROS",
    }
    return mapping.get(txt, txt)


def normalize_impact(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    txt = raw.strip().upper()
    mapping = {
        "BAIXO": "BAIXO",
        "MEDIO": "MEDIO",
        "MÉDIO": "MEDIO",
        "ALTO": "ALTO",
        "MUITO ALTO": "MUITO_ALTO",
        "MUITO_ALTO": "MUITO_ALTO",
        "CRITICO": "CRITICO",
        "CRÍTICO": "CRITICO",
    }
    return mapping.get(txt, txt)


# -----------------------------
# Stubs de serviços externos
# -----------------------------
def glpi_lookup_by_email(email: str) -> Dict[str, Any]:
    """Emula um lookup GLPI. Considera 'casacivil.rs.gov.br' como domínio válido.
    Retorna um dicionário similar ao schema usado nos tópicos.
    """
    if not is_valid_email(email):
        return {"sucesso": False, "erro": "email_invalid"}

    domain = email.split("@")[-1]
    if domain == "casacivil.rs.gov.br":
        return {
            "sucesso": True,
            "resultado": {
                "found": True,
                "user_id": 1234,
                "login": "jonathan-moletta",
                "name": "Jonathan",
                "email": email,
            },
        }
    else:
        return {
            "sucesso": True,
            "resultado": {"found": False},
        }


def create_ticket_stub(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Emula o POST de criação do ticket. Falha se campos obrigatórios faltarem."""
    required = ["title", "description", "category", "impact", "location"]
    for key in required:
        if not payload.get(key):
            return {"sucesso": False, "erro": f"missing_{key}", "trace_id": "stub-0001"}
    return {
        "sucesso": True,
        "ticket_id": 11261,
        "details": payload,
        "trace_id": "stub-11261",
    }


# -----------------------------
# Estados de tópicos (emulação)
# -----------------------------
@dataclass
class EmailTopicOutput:
    validated: bool
    glpi_user_id: Optional[int] = None
    glpi_user_login: Optional[str] = None
    glpi_user_name: Optional[str] = None
    glpi_user_email: Optional[str] = None


@dataclass
class SlotFillOutput:
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    impact: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None


@dataclass
class ConversationState:
    # variáveis que circulariam entre tópicos
    email: Optional[str] = None
    email_output: Optional[EmailTopicOutput] = None
    slots: SlotFillOutput = field(default_factory=SlotFillOutput)


def run_email_topic(max_retries: int = 3) -> EmailTopicOutput:
    """Simula um tópico dedicado ao e-mail com retentativa e opção de prosseguir sem vínculo."""
    retries = 0
    while retries < max_retries:
        email = input("📧 Digite seu e-mail corporativo: ").strip()
        if not is_valid_email(email):
            print("❌ Formato de e-mail inválido. Ex.: nome@empresa.com")
            retries += 1
            continue

        lookup = glpi_lookup_by_email(email)
        if not lookup.get("sucesso"):
            print("❌ Erro ao validar e-mail. Tentar novamente.")
            retries += 1
            continue

        if lookup.get("resultado", {}).get("found"):
            r = lookup["resultado"]
            print(f"✅ Usuário GLPI encontrado: {r['name']} ({r['login']})")
            return EmailTopicOutput(
                validated=True,
                glpi_user_id=r.get("user_id"),
                glpi_user_login=r.get("login"),
                glpi_user_name=r.get("name"),
                glpi_user_email=r.get("email"),
            )
        else:
            print("ℹ️ Usuário não encontrado no GLPI.")
            choice = input("Deseja prosseguir sem vínculo? (s/n): ").strip().lower()
            if choice == "s":
                return EmailTopicOutput(validated=False, glpi_user_email=email)
            else:
                retries += 1

    print("⚠️ Máximo de tentativas atingido. Prosseguindo sem vínculo.")
    # última opção: segue sem vínculo
    return EmailTopicOutput(validated=False)


def run_slot_fill_topic(state: ConversationState) -> SlotFillOutput:
    """Emula preenchimento de slots. Pergunta apenas os faltantes, com validações simples."""
    out = state.slots

    if not out.title:
        out.title = input("📝 Título (obrigatório): ").strip() or None

    if not out.description:
        desc = input("📋 Descrição (mín. 20 chars): ").strip()
        out.description = desc if len(desc) >= 20 else None
        if out.description is None:
            print("❌ Descrição insuficiente. Tente detalhar melhor.")

    if not out.category:
        cat = input("📂 Categoria (ex.: IMPRESSORA, SOFTWARE, REDE): ").strip()
        out.category = normalize_category(cat)

    if not out.impact:
        imp = input("⚡ Impacto (BAIXO, MEDIO, ALTO, MUITO_ALTO, CRITICO): ").strip()
        out.impact = normalize_impact(imp)

    if not out.location:
        out.location = input("📍 Local (obrigatório): ").strip() or None

    if not out.contact_phone:
        phone = input("📞 Telefone (mín. 8 dígitos, opcional): ").strip()
        phone_s = sanitize_phone(phone)
        out.contact_phone = phone_s if is_valid_phone(phone_s) else None

    return out


def run_create_ticket_topic(state: ConversationState) -> Dict[str, Any]:
    """Emula o nó de criação de ticket. Só posta se tudo estiver OK."""
    payload = {
        "title": state.slots.title,
        "description": state.slots.description,
        "category": state.slots.category or "OUTROS",
        "impact": state.slots.impact or "MEDIO",
        "location": state.slots.location,
        "contact_phone": state.slots.contact_phone,
        "requester_email": state.email_output.glpi_user_email
        if state.email_output and state.email_output.glpi_user_email
        else None,
    }
    print("\n⏳ Validando e enviando payload:")
    for k, v in payload.items():
        print(f"  - {k}: {v}")
    result = create_ticket_stub(payload)
    return result


def main():
    print("=== Simulador de fluxo de tópicos (e-mail + slots + criação) ===")

    state = ConversationState()

    # Tópico 1: validação de e-mail
    email_out = run_email_topic(max_retries=3)
    state.email_output = email_out
    print(f"➡️ Saída do tópico de e-mail: {email_out}")

    # Tópico 2: preenchimento de slots
    state.slots = run_slot_fill_topic(state)
    print(f"➡️ Saída do tópico de slots: {state.slots}")

    # Gating simples: exige título, descrição e localização para prosseguir
    required_ok = all([state.slots.title, state.slots.description, state.slots.location])
    if not required_ok:
        print("❌ Campos obrigatórios ausentes. Não é permitido criar o ticket.")
        return

    # Tópico 3: criação do ticket
    result = run_create_ticket_topic(state)
    if result.get("sucesso"):
        print(f"\n✅ Ticket criado! Número: {result['ticket_id']} | Trace: {result['trace_id']}")
    else:
        print(f"\n❌ Falha: {result['erro']} | Trace: {result['trace_id']}")


if __name__ == "__main__":
    main()