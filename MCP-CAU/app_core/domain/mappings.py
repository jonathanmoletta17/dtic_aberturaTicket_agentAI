# -*- coding: utf-8 -*-

IMPACT_MAP = {
    "BAIXO": 1,
    "MEDIO": 2,
    "ALTO": 3,
    "MUITO_ALTO": 4,
    "CRITICO": 5,
}

URGENCY_MAP = {
    "BAIXA": 1,
    "MEDIA": 2,
    "ALTA": 3,
    "MUITO_ALTA": 4,
    "CRITICA": 5,
}

CATEGORY_MAP = {
    "HARDWARE_COMPUTADOR": {
        "display": "🖥️ HARDWARE - Computador/Notebook",
        "glpi_category": "Tipos de computador",
        "glpi_subcategory": "Desktop",
        "glpi_category_id": 1,
    },
    "HARDWARE_IMPRESSORA": {
        "display": "🖨️ HARDWARE - Impressora",
        "glpi_category": "Tipos de impressora",
        "glpi_subcategory": "Impressora laser",
        "glpi_category_id": 2,
    },
    "HARDWARE_MONITOR": {
        "display": "📺 HARDWARE - Monitor/Equipamentos",
        "glpi_category": "Tipos de monitor",
        "glpi_subcategory": "Monitor LCD",
        "glpi_category_id": 3,
    },
    "SOFTWARE": {
        "display": "💻 SOFTWARE - Aplicativos/Programas",
        "glpi_category": "Categorias de software",
        "glpi_subcategory": "Software de escritório",
        "glpi_category_id": 4,
    },
    "CONECTIVIDADE": {
        "display": "🌐 CONECTIVIDADE - Internet/Rede",
        "glpi_category": "Redes",
        "glpi_subcategory": "Redes WiFi",
        "glpi_category_id": 5,
    },
    "SEGURANCA": {
        "display": "🔐 SEGURANÇA - Acesso/Login",
        "glpi_category": "Categorias ITIL",
        "glpi_subcategory": "Gestão de identidade",
        "glpi_category_id": 6,
    },
    "SOLICITACAO": {
        "display": "📋 SOLICITAÇÃO - Instalação/Configuração",
        "glpi_category": "Assistência",
        "glpi_subcategory": "Instalação de software",
        "glpi_category_id": 7,
    },
    "OUTROS": {
        "display": "❓ OUTROS - Não listado acima",
        "glpi_category": "Geral",
        "glpi_subcategory": "Problemas diversos",
        "glpi_category_id": 8,
    },
}


