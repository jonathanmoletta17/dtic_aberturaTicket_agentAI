# -*- coding: utf-8 -*-
"""
Teste isolado para validar mapeamento de impacto/urgência e cálculo de prioridade
sem alterar o código de produção. Compara lógica atual vs. proposta corrigida.
"""

import os
import sys

# Tornar o pacote app_core importável
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app_core.domain.mappings import IMPACT_MAP as CURRENT_IMPACT_MAP, URGENCY_MAP as CURRENT_URGENCY_MAP


# Rótulos GLPI por ID (referência visual)
GLPI_PRIORITY_LABEL = {
    1: "Muito baixa",
    2: "Baixa",
    3: "Média",
    4: "Alta",
    5: "Muito alta",
}


def current_priority(impact_raw: str, urgency_raw: str | None) -> tuple[int, int, int]:
    impact_key = (impact_raw or "MEDIO").upper()
    urgency_key = (urgency_raw or "MEDIA").upper()
    impact_id = CURRENT_IMPACT_MAP.get(impact_key, 2)
    urgency_id = CURRENT_URGENCY_MAP.get(urgency_key, 2)
    priority_id = min(5, max(1, (impact_id + urgency_id) // 2))
    return impact_id, urgency_id, priority_id


# Proposta corrigida: alinhar escala ao GLPI e priorizar o maior entre impacto/urgência
PROPOSED_IMPACT_MAP = {
    "BAIXO": 2,
    "MEDIO": 3,
    "ALTO": 4,
    "MUITO_ALTO": 5,
    "CRITICO": 5,  # manter no topo
}

PROPOSED_URGENCY_MAP = {
    "BAIXA": 2,
    "MEDIA": 3,
    "ALTA": 4,
    "MUITO_ALTA": 5,
    "CRITICA": 5,
}


def proposed_priority(impact_raw: str, urgency_raw: str | None) -> tuple[int, int, int]:
    impact_key = (impact_raw or "MEDIO").upper()
    # Se urgência não vier, usar impacto como base para urgência
    urgency_key = ((urgency_raw or impact_raw or "MEDIO")).upper()
    impact_id = PROPOSED_IMPACT_MAP.get(impact_key, 3)
    urgency_id = PROPOSED_URGENCY_MAP.get(urgency_key, 3)
    priority_id = max(impact_id, urgency_id)
    return impact_id, urgency_id, priority_id


def run_cases():
    cases = [
        {"impact": "ALTO", "urgency": None},
        {"impact": "ALTO", "urgency": "MEDIA"},
        {"impact": "MEDIO", "urgency": None},
        {"impact": "BAIXO", "urgency": "MEDIA"},
        {"impact": "CRITICO", "urgency": "ALTA"},
    ]

    print("\n=== Validação de Mapeamento de Prioridade (Atual vs. Proposta) ===\n")
    print(f"{'Impacto':<10} {'Urgência':<10} | Atual(i,u,p) -> Label | Proposta(i,u,p) -> Label")
    print("-" * 80)

    for c in cases:
        i_raw, u_raw = c["impact"], c["urgency"]
        ci, cu, cp = current_priority(i_raw, u_raw)
        clabel = GLPI_PRIORITY_LABEL.get(cp)
        pi, pu, pp = proposed_priority(i_raw, u_raw)
        plabel = GLPI_PRIORITY_LABEL.get(pp)
        print(f"{i_raw:<10} {str(u_raw or '-'):<10} | ({ci},{cu},{cp}) -> {clabel:<11} | ({pi},{pu},{pp}) -> {plabel}")


if __name__ == "__main__":
    run_cases()