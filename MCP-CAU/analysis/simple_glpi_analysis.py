#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações do GLPI
GLPI_URL = os.getenv("GLPI_URL")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

def autenticar_glpi():
    """Autentica no GLPI usando a mesma lógica do app.py"""
    headers = {
        "App-Token": GLPI_APP_TOKEN,
        "Authorization": f"user_token {GLPI_USER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(
            f"{GLPI_URL}/initSession", 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        session_token = data.get("session_token")
        
        if not session_token:
            raise RuntimeError("Session token não encontrado na resposta do GLPI")
            
        return {
            "App-Token": GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }
        
    except Exception as e:
        print(f"❌ Erro na autenticação GLPI: {str(e)}")
        return None

def buscar_tickets(headers, limit=50):
    """Busca tickets do GLPI"""
    try:
        # Tenta buscar tickets com range menor primeiro
        response = requests.get(
            f"{GLPI_URL}/Ticket?range=0-{min(limit-1, 19)}",
            headers=headers,
            timeout=30
        )
        
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code in [200, 206]:  # 206 = Partial Content (normal para range)
            try:
                data = response.json()
                print(f"Tipo de dados recebidos: {type(data)}")
                if isinstance(data, list):
                    print(f"Número de tickets recebidos: {len(data)}")
                    return data
                else:
                    print(f"Dados não são uma lista: {data}")
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {str(e)}")
                print(f"Primeiros 500 caracteres da resposta: {response.text[:500]}")
                return None
        else:
            print(f"❌ Erro ao buscar tickets: {response.status_code}")
            print(f"Resposta: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao buscar tickets: {str(e)}")
        return None

def analisar_descricoes(tickets):
    """Analisa as descrições dos tickets"""
    problemas = {
        'muito_curtas': [],
        'vagas': [],
        'sem_contexto': [],
        'bem_descritas': []
    }
    
    palavras_vagas = ['problema', 'erro', 'não funciona', 'quebrou', 'parou', 'ruim', 'lento']
    
    for ticket in tickets:
        descricao = ticket.get('content', '').lower()
        titulo = ticket.get('name', '').lower()
        ticket_id = ticket.get('id', 'N/A')
        
        # Muito curtas (menos de 20 caracteres)
        if len(descricao) < 20:
            problemas['muito_curtas'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao,
                'tamanho': len(descricao)
            })
        
        # Descrições vagas
        elif any(palavra in descricao for palavra in palavras_vagas):
            problemas['vagas'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao[:100] + '...' if len(descricao) > 100 else descricao
            })
        
        # Sem contexto (apenas uma palavra ou frase muito simples)
        elif len(descricao.split()) < 5:
            problemas['sem_contexto'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao
            })
        
        # Bem descritas
        else:
            problemas['bem_descritas'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao[:100] + '...' if len(descricao) > 100 else descricao
            })
    
    return problemas

def analisar_categorias(tickets):
    """Analisa a distribuição de categorias"""
    categorias = {}
    sem_categoria = 0
    
    for ticket in tickets:
        cat_id = ticket.get('itilcategories_id', 0)
        if cat_id == 0 or cat_id is None:
            sem_categoria += 1
        else:
            categorias[cat_id] = categorias.get(cat_id, 0) + 1
    
    return {
        'distribuicao': categorias,
        'sem_categoria': sem_categoria,
        'total': len(tickets)
    }

def gerar_relatorio(tickets, problemas_desc, analise_cat):
    """Gera relatório da análise"""
    total_tickets = len(tickets)
    
    relatorio = {
        'resumo_geral': {
            'total_tickets_analisados': total_tickets,
            'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'problemas_descricao': {
            'muito_curtas': {
                'quantidade': len(problemas_desc['muito_curtas']),
                'percentual': round(len(problemas_desc['muito_curtas']) / total_tickets * 100, 2),
                'exemplos': problemas_desc['muito_curtas'][:5]
            },
            'vagas': {
                'quantidade': len(problemas_desc['vagas']),
                'percentual': round(len(problemas_desc['vagas']) / total_tickets * 100, 2),
                'exemplos': problemas_desc['vagas'][:5]
            },
            'sem_contexto': {
                'quantidade': len(problemas_desc['sem_contexto']),
                'percentual': round(len(problemas_desc['sem_contexto']) / total_tickets * 100, 2),
                'exemplos': problemas_desc['sem_contexto'][:5]
            },
            'bem_descritas': {
                'quantidade': len(problemas_desc['bem_descritas']),
                'percentual': round(len(problemas_desc['bem_descritas']) / total_tickets * 100, 2),
                'exemplos': problemas_desc['bem_descritas'][:3]
            }
        },
        'analise_categorias': analise_cat,
        'recomendacoes': [
            "Implementar validação de tamanho mínimo para descrições (mínimo 30 caracteres)",
            "Adicionar perguntas direcionadas baseadas na categoria selecionada",
            "Criar templates de descrição para categorias mais comuns",
            "Implementar sugestões automáticas durante a digitação",
            "Adicionar campo obrigatório para 'Passos para reproduzir o problema'",
            "Criar validação para evitar palavras muito genéricas",
            "Implementar sistema de tags para melhor categorização"
        ]
    }
    
    return relatorio

def main():
    print("🚀 ANÁLISE SIMPLIFICADA DE TICKETS GLPI")
    print("=" * 50)
    
    # Autenticação
    headers = autenticar_glpi()
    if not headers:
        return
    
    print("✅ Autenticado no GLPI com sucesso")
    
    # Buscar tickets
    print("📋 Buscando tickets...")
    tickets = buscar_tickets(headers, limit=100)
    
    if not tickets:
        print("❌ Não foi possível buscar tickets")
        return
    
    print(f"✅ Encontrados {len(tickets)} tickets")
    
    # Análises
    print("🔍 Analisando descrições...")
    problemas_desc = analisar_descricoes(tickets)
    
    print("📊 Analisando categorias...")
    analise_cat = analisar_categorias(tickets)
    
    # Gerar relatório
    print("📝 Gerando relatório...")
    relatorio = gerar_relatorio(tickets, problemas_desc, analise_cat)
    
    # Salvar relatório
    with open('relatorio_glpi_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    # Exibir resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA ANÁLISE")
    print("=" * 50)
    print(f"Total de tickets analisados: {relatorio['resumo_geral']['total_tickets_analisados']}")
    print(f"Descrições muito curtas: {relatorio['problemas_descricao']['muito_curtas']['quantidade']} ({relatorio['problemas_descricao']['muito_curtas']['percentual']}%)")
    print(f"Descrições vagas: {relatorio['problemas_descricao']['vagas']['quantidade']} ({relatorio['problemas_descricao']['vagas']['percentual']}%)")
    print(f"Descrições sem contexto: {relatorio['problemas_descricao']['sem_contexto']['quantidade']} ({relatorio['problemas_descricao']['sem_contexto']['percentual']}%)")
    print(f"Descrições bem feitas: {relatorio['problemas_descricao']['bem_descritas']['quantidade']} ({relatorio['problemas_descricao']['bem_descritas']['percentual']}%)")
    print(f"Tickets sem categoria: {analise_cat['sem_categoria']}")
    
    print(f"\n✅ Relatório completo salvo em: relatorio_glpi_analysis.json")

if __name__ == "__main__":
    main()