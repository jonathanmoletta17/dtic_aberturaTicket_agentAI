#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
import re
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# Configurações do GLPI
GLPI_URL = os.getenv("GLPI_URL")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

def autenticar_glpi():
    """Autentica no GLPI"""
    headers = {
        "App-Token": GLPI_APP_TOKEN,
        "Authorization": f"user_token {GLPI_USER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(f"{GLPI_URL}/initSession", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        session_token = data.get("session_token")
        
        if not session_token:
            raise RuntimeError("Session token não encontrado")
            
        return {
            "App-Token": GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }
        
    except Exception as e:
        print(f"❌ Erro na autenticação: {str(e)}")
        return None

def buscar_mais_tickets(headers):
    """Busca mais tickets em lotes para análise mais completa"""
    todos_tickets = []
    
    # Busca em lotes de 20
    for start in range(0, 100, 20):
        try:
            response = requests.get(
                f"{GLPI_URL}/Ticket?range={start}-{start+19}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 206]:
                tickets = response.json()
                if tickets:
                    todos_tickets.extend(tickets)
                    print(f"✅ Coletados {len(tickets)} tickets (lote {start//20 + 1})")
                else:
                    break
            else:
                print(f"⚠️  Erro no lote {start//20 + 1}: {response.status_code}")
                break
                
        except Exception as e:
            print(f"⚠️  Erro no lote {start//20 + 1}: {str(e)}")
            break
    
    return todos_tickets

def limpar_html(texto):
    """Remove tags HTML e decodifica entidades"""
    if not texto:
        return ""
    
    # Decodifica entidades HTML
    texto = texto.replace("&#60;", "<").replace("&#62;", ">")
    texto = texto.replace("&lt;", "<").replace("&gt;", ">")
    texto = texto.replace("&amp;", "&").replace("&quot;", '"')
    
    # Remove tags HTML
    texto = re.sub(r'<[^>]+>', '', texto)
    
    # Remove quebras de linha excessivas e espaços
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def analisar_problemas_detalhados(tickets):
    """Análise detalhada dos problemas nos tickets"""
    problemas = {
        'descricoes_muito_curtas': [],
        'descricoes_vagas': [],
        'descricoes_sem_contexto': [],
        'titulos_genericos': [],
        'falta_informacoes_tecnicas': [],
        'categorias_mais_usadas': Counter(),
        'palavras_mais_comuns': Counter(),
        'padroes_problematicos': []
    }
    
    # Palavras que indicam descrições vagas
    palavras_vagas = [
        'problema', 'erro', 'não funciona', 'quebrou', 'parou', 'ruim', 'lento',
        'travou', 'bugou', 'deu pau', 'não vai', 'não abre', 'não carrega'
    ]
    
    # Títulos genéricos comuns
    titulos_genericos = [
        'problema', 'erro', 'ajuda', 'suporte', 'dúvida', 'questão',
        'solicitação', 'pedido', 'urgente', 'importante'
    ]
    
    for ticket in tickets:
        ticket_id = ticket.get('id', 'N/A')
        titulo = ticket.get('name', '').lower()
        descricao_raw = ticket.get('content', '')
        descricao = limpar_html(descricao_raw).lower()
        categoria_id = ticket.get('itilcategories_id', 0)
        
        # Contabiliza categorias
        problemas['categorias_mais_usadas'][categoria_id] += 1
        
        # Analisa palavras na descrição
        palavras = re.findall(r'\b\w+\b', descricao)
        problemas['palavras_mais_comuns'].update(palavras)
        
        # Descrições muito curtas
        if len(descricao) < 20:
            problemas['descricoes_muito_curtas'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao,
                'tamanho': len(descricao)
            })
        
        # Descrições vagas
        if any(palavra in descricao for palavra in palavras_vagas):
            problemas['descricoes_vagas'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao[:100] + '...' if len(descricao) > 100 else descricao,
                'palavras_vagas': [p for p in palavras_vagas if p in descricao]
            })
        
        # Descrições sem contexto
        if len(palavras) < 5:
            problemas['descricoes_sem_contexto'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao,
                'num_palavras': len(palavras)
            })
        
        # Títulos genéricos
        if any(termo in titulo for termo in titulos_genericos):
            problemas['titulos_genericos'].append({
                'id': ticket_id,
                'titulo': titulo,
                'termos_genericos': [t for t in titulos_genericos if t in titulo]
            })
        
        # Falta de informações técnicas (sem detalhes específicos)
        indicadores_tecnicos = [
            'versão', 'sistema', 'aplicativo', 'programa', 'arquivo', 'pasta',
            'erro', 'mensagem', 'código', 'ip', 'rede', 'servidor', 'computador'
        ]
        
        if len(descricao) > 20 and not any(ind in descricao for ind in indicadores_tecnicos):
            problemas['falta_informacoes_tecnicas'].append({
                'id': ticket_id,
                'titulo': titulo,
                'descricao': descricao[:100] + '...' if len(descricao) > 100 else descricao
            })
    
    return problemas

def gerar_recomendacoes_especificas(problemas, total_tickets):
    """Gera recomendações específicas baseadas nos problemas encontrados"""
    recomendacoes = []
    
    # Análise de descrições curtas
    pct_curtas = (len(problemas['descricoes_muito_curtas']) / total_tickets) * 100
    if pct_curtas > 10:
        recomendacoes.append({
            'problema': f'{pct_curtas:.1f}% das descrições são muito curtas (< 20 caracteres)',
            'solucao': 'Implementar validação de tamanho mínimo de 50 caracteres para descrições',
            'implementacao': 'Adicionar validação no Copilot Studio antes de enviar o ticket'
        })
    
    # Análise de descrições vagas
    pct_vagas = (len(problemas['descricoes_vagas']) / total_tickets) * 100
    if pct_vagas > 5:
        recomendacoes.append({
            'problema': f'{pct_vagas:.1f}% das descrições contêm termos muito vagos',
            'solucao': 'Criar perguntas direcionadas para evitar termos genéricos',
            'implementacao': 'Quando detectar palavras vagas, fazer perguntas específicas como "Qual mensagem de erro aparece?" ou "Em que momento isso acontece?"'
        })
    
    # Análise de títulos genéricos
    pct_titulos = (len(problemas['titulos_genericos']) / total_tickets) * 100
    if pct_titulos > 15:
        recomendacoes.append({
            'problema': f'{pct_titulos:.1f}% dos títulos são muito genéricos',
            'solucao': 'Implementar sugestões automáticas de títulos baseadas na categoria',
            'implementacao': 'Criar templates de títulos por categoria (ex: "Hardware - [Equipamento] - [Problema]")'
        })
    
    # Análise de falta de informações técnicas
    pct_sem_info = (len(problemas['falta_informacoes_tecnicas']) / total_tickets) * 100
    if pct_sem_info > 20:
        recomendacoes.append({
            'problema': f'{pct_sem_info:.1f}% dos tickets não têm informações técnicas suficientes',
            'solucao': 'Adicionar campos obrigatórios específicos por categoria',
            'implementacao': 'Para hardware: modelo/marca; Para software: versão/nome; Para rede: localização/equipamento'
        })
    
    # Análise das categorias mais usadas
    top_categorias = problemas['categorias_mais_usadas'].most_common(3)
    if top_categorias:
        recomendacoes.append({
            'problema': f'Categorias mais usadas: {[f"ID {cat[0]} ({cat[1]} tickets)" for cat in top_categorias]}',
            'solucao': 'Criar fluxos específicos para as categorias mais comuns',
            'implementacao': 'Desenvolver templates e perguntas específicas para essas categorias'
        })
    
    return recomendacoes

def main():
    print("🔍 ANÁLISE DETALHADA DE PROBLEMAS - TICKETS GLPI")
    print("=" * 60)
    
    # Autenticação
    headers = autenticar_glpi()
    if not headers:
        return
    
    print("✅ Autenticado no GLPI")
    
    # Buscar mais tickets
    print("📋 Buscando tickets em lotes...")
    tickets = buscar_mais_tickets(headers)
    
    if not tickets:
        print("❌ Não foi possível buscar tickets")
        return
    
    print(f"✅ Total de {len(tickets)} tickets coletados")
    
    # Análise detalhada
    print("🔍 Executando análise detalhada...")
    problemas = analisar_problemas_detalhados(tickets)
    
    # Gerar recomendações
    print("💡 Gerando recomendações específicas...")
    recomendacoes = gerar_recomendacoes_especificas(problemas, len(tickets))
    
    # Relatório final
    relatorio_detalhado = {
        'resumo': {
            'total_tickets': len(tickets),
            'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'problemas_identificados': {
            'descricoes_muito_curtas': {
                'quantidade': len(problemas['descricoes_muito_curtas']),
                'percentual': round(len(problemas['descricoes_muito_curtas']) / len(tickets) * 100, 2),
                'exemplos': problemas['descricoes_muito_curtas'][:3]
            },
            'descricoes_vagas': {
                'quantidade': len(problemas['descricoes_vagas']),
                'percentual': round(len(problemas['descricoes_vagas']) / len(tickets) * 100, 2),
                'exemplos': problemas['descricoes_vagas'][:3]
            },
            'titulos_genericos': {
                'quantidade': len(problemas['titulos_genericos']),
                'percentual': round(len(problemas['titulos_genericos']) / len(tickets) * 100, 2),
                'exemplos': problemas['titulos_genericos'][:3]
            },
            'falta_informacoes_tecnicas': {
                'quantidade': len(problemas['falta_informacoes_tecnicas']),
                'percentual': round(len(problemas['falta_informacoes_tecnicas']) / len(tickets) * 100, 2),
                'exemplos': problemas['falta_informacoes_tecnicas'][:3]
            }
        },
        'estatisticas': {
            'categorias_mais_usadas': dict(problemas['categorias_mais_usadas'].most_common(10)),
            'palavras_mais_comuns': dict(problemas['palavras_mais_comuns'].most_common(20))
        },
        'recomendacoes_especificas': recomendacoes
    }
    
    # Salvar relatório
    with open('relatorio_detalhado_glpi.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio_detalhado, f, ensure_ascii=False, indent=2)
    
    # Exibir resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA ANÁLISE DETALHADA")
    print("=" * 60)
    print(f"Total de tickets analisados: {len(tickets)}")
    print(f"Descrições muito curtas: {len(problemas['descricoes_muito_curtas'])} ({round(len(problemas['descricoes_muito_curtas']) / len(tickets) * 100, 1)}%)")
    print(f"Descrições vagas: {len(problemas['descricoes_vagas'])} ({round(len(problemas['descricoes_vagas']) / len(tickets) * 100, 1)}%)")
    print(f"Títulos genéricos: {len(problemas['titulos_genericos'])} ({round(len(problemas['titulos_genericos']) / len(tickets) * 100, 1)}%)")
    print(f"Falta info técnica: {len(problemas['falta_informacoes_tecnicas'])} ({round(len(problemas['falta_informacoes_tecnicas']) / len(tickets) * 100, 1)}%)")
    
    print(f"\n🔝 Top 3 categorias:")
    for cat_id, count in problemas['categorias_mais_usadas'].most_common(3):
        print(f"   Categoria {cat_id}: {count} tickets")
    
    print(f"\n💡 {len(recomendacoes)} recomendações específicas geradas")
    print(f"\n✅ Relatório detalhado salvo em: relatorio_detalhado_glpi.json")

if __name__ == "__main__":
    main()