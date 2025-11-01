# analyze_glpi_patterns.py - Análise de Padrões de Chamados GLPI
import os
import requests
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configurações do GLPI
GLPI_URL = os.getenv("GLPI_URL")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

class GLPIAnalyzer:
    def __init__(self):
        self.session_token = None
        self.tickets = []
        self.categories = {}
        self.analysis_results = {}
        
    def authenticate(self):
        """Autentica no GLPI"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"user_token {GLPI_USER_TOKEN}",
                "App-Token": GLPI_APP_TOKEN
            }
            
            response = requests.get(f"{GLPI_URL}/initSession", headers=headers)
            response.raise_for_status()
            
            result = response.json()
            self.session_token = result.get("session_token")
            print(f"✅ Autenticado no GLPI com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro na autenticação: {str(e)}")
            return False
    
    def get_headers(self):
        """Retorna headers para requisições autenticadas"""
        return {
            "Content-Type": "application/json",
            "Session-Token": self.session_token,
            "App-Token": GLPI_APP_TOKEN
        }
    
    def fetch_tickets(self, limit=100):
        """Busca tickets recentes do GLPI"""
        try:
            headers = self.get_headers()
            
            # Tenta diferentes formas de buscar tickets
            attempts = [
                # Tentativa 1: Com parâmetros completos
                {
                    'url': f"{GLPI_URL}/Ticket",
                    'params': {
                        'range': f'0-{limit-1}',
                        'sort': 'id',
                        'order': 'DESC'
                    }
                },
                # Tentativa 2: Apenas com range
                {
                    'url': f"{GLPI_URL}/Ticket",
                    'params': {
                        'range': f'0-{limit-1}'
                    }
                },
                # Tentativa 3: Sem parâmetros
                {
                    'url': f"{GLPI_URL}/Ticket",
                    'params': {}
                }
            ]
            
            for attempt in attempts:
                try:
                    response = requests.get(attempt['url'], headers=headers, params=attempt['params'])
                    if response.status_code == 200:
                        tickets_data = response.json()
                        # Se retornou uma lista, usa diretamente, senão tenta extrair
                        if isinstance(tickets_data, list):
                            self.tickets = tickets_data[:limit]
                        elif isinstance(tickets_data, dict) and 'data' in tickets_data:
                            self.tickets = tickets_data['data'][:limit]
                        else:
                            self.tickets = [tickets_data] if tickets_data else []
                        
                        print(f"✅ Coletados {len(self.tickets)} tickets")
                        return True
                except Exception as e:
                    print(f"⚠️  Tentativa falhou: {str(e)}")
                    continue
            
            print(f"❌ Não foi possível buscar tickets")
            return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar tickets: {str(e)}")
            return False
    
    def fetch_categories(self):
        """Busca categorias do GLPI"""
        try:
            headers = self.get_headers()
            
            # Tenta diferentes endpoints para categorias
            endpoints = [
                f"{GLPI_URL}/ITILCategory",
                f"{GLPI_URL}/itilcategory", 
                f"{GLPI_URL}/ItilCategory"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers)
                    if response.status_code == 200:
                        categories_data = response.json()
                        for cat in categories_data:
                            self.categories[cat.get('id')] = cat.get('name', 'Sem categoria')
                        print(f"✅ Coletadas {len(self.categories)} categorias")
                        return True
                except:
                    continue
            
            print(f"⚠️  Não foi possível buscar categorias, continuando sem elas")
            return True  # Continua a análise mesmo sem categorias
                
        except Exception as e:
            print(f"⚠️  Erro ao buscar categorias: {str(e)}, continuando sem elas")
            return True  # Continua a análise mesmo sem categorias
    
    def analyze_descriptions(self):
        """Analisa padrões nas descrições dos chamados"""
        print("\n🔍 ANÁLISE DE DESCRIÇÕES")
        print("=" * 50)
        
        descriptions = []
        short_descriptions = []
        vague_descriptions = []
        missing_info = []
        
        # Palavras que indicam descrições vagas
        vague_indicators = [
            'não funciona', 'com problema', 'não está funcionando', 'quebrado',
            'parou', 'travou', 'lento', 'erro', 'problema', 'ajuda', 'urgente'
        ]
        
        # Informações importantes que podem estar faltando
        important_info = [
            'local', 'sala', 'andar', 'prédio', 'setor',
            'telefone', 'contato', 'ramal',
            'erro', 'mensagem', 'código',
            'quando', 'horário', 'desde quando'
        ]
        
        for ticket in self.tickets:
            content = ticket.get('content', '').lower()
            name = ticket.get('name', '').lower()
            full_text = f"{name} {content}"
            
            descriptions.append(len(content))
            
            # Verifica descrições muito curtas (menos de 20 caracteres)
            if len(content) < 20:
                short_descriptions.append({
                    'id': ticket.get('id'),
                    'name': ticket.get('name'),
                    'content': ticket.get('content'),
                    'length': len(content)
                })
            
            # Verifica descrições vagas
            vague_count = sum(1 for indicator in vague_indicators if indicator in full_text)
            if vague_count > 0 and len(content) < 50:
                vague_descriptions.append({
                    'id': ticket.get('id'),
                    'name': ticket.get('name'),
                    'content': ticket.get('content'),
                    'vague_indicators': vague_count
                })
            
            # Verifica informações faltantes
            missing_count = sum(1 for info in important_info if info not in full_text)
            if missing_count > 6:  # Se faltam mais de 6 tipos de informação
                missing_info.append({
                    'id': ticket.get('id'),
                    'name': ticket.get('name'),
                    'content': ticket.get('content'),
                    'missing_score': missing_count
                })
        
        # Estatísticas
        avg_length = sum(descriptions) / len(descriptions) if descriptions else 0
        
        self.analysis_results['descriptions'] = {
            'total_tickets': len(self.tickets),
            'average_length': round(avg_length, 2),
            'short_descriptions': len(short_descriptions),
            'vague_descriptions': len(vague_descriptions),
            'missing_info': len(missing_info),
            'examples': {
                'short': short_descriptions[:5],
                'vague': vague_descriptions[:5],
                'missing': missing_info[:5]
            }
        }
        
        print(f"📊 Total de tickets analisados: {len(self.tickets)}")
        print(f"📏 Comprimento médio das descrições: {avg_length:.1f} caracteres")
        print(f"⚠️  Descrições muito curtas (<20 chars): {len(short_descriptions)} ({len(short_descriptions)/len(self.tickets)*100:.1f}%)")
        print(f"🤔 Descrições vagas: {len(vague_descriptions)} ({len(vague_descriptions)/len(self.tickets)*100:.1f}%)")
        print(f"❓ Faltam informações importantes: {len(missing_info)} ({len(missing_info)/len(self.tickets)*100:.1f}%)")
    
    def analyze_categories(self):
        """Analisa padrões de categorização"""
        print("\n📂 ANÁLISE DE CATEGORIZAÇÃO")
        print("=" * 50)
        
        category_usage = Counter()
        uncategorized = 0
        
        for ticket in self.tickets:
            cat_id = ticket.get('itilcategories_id')
            if cat_id and cat_id != '0':
                category_name = self.categories.get(int(cat_id), f'ID:{cat_id}')
                category_usage[category_name] += 1
            else:
                uncategorized += 1
        
        self.analysis_results['categories'] = {
            'total_categories': len(category_usage),
            'uncategorized': uncategorized,
            'most_used': category_usage.most_common(10),
            'distribution': dict(category_usage)
        }
        
        print(f"📊 Categorias utilizadas: {len(category_usage)}")
        print(f"❌ Chamados sem categoria: {uncategorized} ({uncategorized/len(self.tickets)*100:.1f}%)")
        print(f"\n🏆 Top 5 categorias mais usadas:")
        for i, (category, count) in enumerate(category_usage.most_common(5), 1):
            percentage = count/len(self.tickets)*100
            print(f"   {i}. {category}: {count} tickets ({percentage:.1f}%)")
    
    def analyze_impact_urgency(self):
        """Analisa padrões de impacto e urgência"""
        print("\n⚡ ANÁLISE DE IMPACTO E URGÊNCIA")
        print("=" * 50)
        
        impact_map = {1: 'Muito Baixo', 2: 'Baixo', 3: 'Médio', 4: 'Alto', 5: 'Muito Alto'}
        urgency_map = {1: 'Muito Baixa', 2: 'Baixa', 3: 'Média', 4: 'Alta', 5: 'Muito Alta'}
        
        impact_usage = Counter()
        urgency_usage = Counter()
        priority_usage = Counter()
        
        for ticket in self.tickets:
            impact = ticket.get('impact', 0)
            urgency = ticket.get('urgency', 0)
            priority = ticket.get('priority', 0)
            
            impact_usage[impact_map.get(impact, f'ID:{impact}')] += 1
            urgency_usage[urgency_map.get(urgency, f'ID:{urgency}')] += 1
            priority_usage[priority] += 1
        
        self.analysis_results['impact_urgency'] = {
            'impact_distribution': dict(impact_usage),
            'urgency_distribution': dict(urgency_usage),
            'priority_distribution': dict(priority_usage)
        }
        
        print("📊 Distribuição de Impacto:")
        for impact, count in impact_usage.most_common():
            percentage = count/len(self.tickets)*100
            print(f"   {impact}: {count} tickets ({percentage:.1f}%)")
        
        print("\n📊 Distribuição de Urgência:")
        for urgency, count in urgency_usage.most_common():
            percentage = count/len(self.tickets)*100
            print(f"   {urgency}: {count} tickets ({percentage:.1f}%)")
    
    def generate_recommendations(self):
        """Gera recomendações baseadas na análise"""
        print("\n💡 RECOMENDAÇÕES PARA MELHORIA")
        print("=" * 50)
        
        recommendations = []
        
        # Análise de descrições
        desc_data = self.analysis_results.get('descriptions', {})
        short_pct = (desc_data.get('short_descriptions', 0) / desc_data.get('total_tickets', 1)) * 100
        vague_pct = (desc_data.get('vague_descriptions', 0) / desc_data.get('total_tickets', 1)) * 100
        
        if short_pct > 20:
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Descrições',
                'issue': f'{short_pct:.1f}% das descrições são muito curtas',
                'solution': 'Implementar perguntas direcionadas e templates por categoria'
            })
        
        if vague_pct > 15:
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Descrições',
                'issue': f'{vague_pct:.1f}% das descrições são vagas',
                'solution': 'Adicionar perguntas específicas sobre sintomas e contexto'
            })
        
        # Análise de categorização
        cat_data = self.analysis_results.get('categories', {})
        uncat_pct = (cat_data.get('uncategorized', 0) / desc_data.get('total_tickets', 1)) * 100
        
        if uncat_pct > 10:
            recommendations.append({
                'priority': 'MÉDIA',
                'category': 'Categorização',
                'issue': f'{uncat_pct:.1f}% dos chamados não têm categoria',
                'solution': 'Tornar a seleção de categoria obrigatória com opções claras'
            })
        
        self.analysis_results['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. 🔴 {rec['priority']} - {rec['category']}")
            print(f"   Problema: {rec['issue']}")
            print(f"   Solução: {rec['solution']}\n")
    
    def save_results(self):
        """Salva resultados da análise em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"glpi_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos em: {filename}")
    
    def run_analysis(self):
        """Executa análise completa"""
        print("🚀 INICIANDO ANÁLISE DE PADRÕES GLPI")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        if not self.fetch_categories():
            return False
        
        if not self.fetch_tickets():
            return False
        
        self.analyze_descriptions()
        self.analyze_categories()
        self.analyze_impact_urgency()
        self.generate_recommendations()
        self.save_results()
        
        print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        return True

if __name__ == "__main__":
    analyzer = GLPIAnalyzer()
    analyzer.run_analysis()