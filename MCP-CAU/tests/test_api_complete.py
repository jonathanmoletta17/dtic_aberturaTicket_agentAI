#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de testes automatizados para validação completa da API de criação de tickets
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sys

# Configurações
BASE_URL = "http://localhost:5000"
HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json'
}

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def add_test(self, name, passed, details=""):
        self.tests.append({
            'name': name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*80)
        print(f"RESUMO DOS TESTES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(f"Total de testes: {len(self.tests)}")
        print(f"Aprovados: {self.passed}")
        print(f"Falharam: {self.failed}")
        print(f"Taxa de sucesso: {(self.passed/len(self.tests)*100):.1f}%")
        print("\nDetalhes dos testes:")
        print("-"*80)
        
        for test in self.tests:
            status = "✅ PASSOU" if test['passed'] else "❌ FALHOU"
            print(f"{status} - {test['name']}")
            if test['details']:
                print(f"    Detalhes: {test['details']}")
        print("="*80)

def test_health_check(results):
    """Teste 1: Verificar health check"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('glpi_configured') and data.get('status') == 'ok':
                results.add_test("Health Check", True, "GLPI configurado e funcionando")
            else:
                results.add_test("Health Check", False, f"GLPI não configurado: {data}")
        else:
            results.add_test("Health Check", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Health Check", False, f"Erro: {str(e)}")

def test_missing_fields(results):
    """Teste 2: Validação de campos obrigatórios"""
    test_cases = [
        ({}, "Dados vazios"),
        ({"titulo": "Teste"}, "Sem descrição"),
        ({"descricao": "Teste"}, "Sem título"),
        ({"titulo": "Teste", "descricao": "Teste"}, "Sem categoria"),
        ({"titulo": "Teste", "descricao": "Teste", "categoria": "Hardware"}, "Sem impacto"),
        ({"titulo": "Teste", "descricao": "Teste", "categoria": "Hardware", "impacto": "Alto"}, "Sem localização"),
    ]
    
    for data, description in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/create-ticket-complete",
                headers=HEADERS,
                json=data,
                timeout=10
            )
            
            if response.status_code == 400:
                response_data = response.json()
                if not response_data.get('sucesso', True):
                    results.add_test(f"Validação: {description}", True, "Campo obrigatório detectado corretamente")
                else:
                    results.add_test(f"Validação: {description}", False, "Deveria ter falhado mas passou")
            else:
                results.add_test(f"Validação: {description}", False, f"Status inesperado: {response.status_code}")
        except Exception as e:
            results.add_test(f"Validação: {description}", False, f"Erro: {str(e)}")

def test_valid_ticket_creation(results):
    """Teste 3: Criação de ticket válido"""
    ticket_data = {
        "title": f"Teste Automatizado - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "Este é um ticket de teste criado automaticamente para validar o sistema. Contém caracteres especiais: áéíóú çñü",
        "category": "HARDWARE_COMPUTADOR",
        "impact": "ALTO",
        "location": "Sala de TI - Andar 3",
        "contact_phone": "(51) 99999-9999"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/create-ticket-complete",
            headers=HEADERS,
            json=ticket_data,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('sucesso'):
                ticket_id = data.get('ticket_id')
                trace_id = data.get('trace_id')
                results.add_test("Criação de Ticket Válido", True, 
                               f"Ticket ID: {ticket_id}, Trace ID: {trace_id}")
                return ticket_id, trace_id
            else:
                results.add_test("Criação de Ticket Válido", False, 
                               f"Falha na criação: {data.get('erro', 'Erro desconhecido')}")
        else:
            results.add_test("Criação de Ticket Válido", False, 
                           f"Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results.add_test("Criação de Ticket Válido", False, f"Erro: {str(e)}")
    
    return None, None

def test_response_format(results):
    """Teste 4: Validação do formato de resposta"""
    ticket_data = {
        "title": "Teste Formato Resposta",
        "description": "Validando formato da resposta",
        "category": "SOFTWARE",
        "impact": "MEDIO",
        "location": "Local de Teste",
        "contact_phone": "(51) 88888-8888"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/create-ticket-complete",
            headers=HEADERS,
            json=ticket_data,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            required_fields = ['sucesso', 'ticket_id', 'categoria', 'trace_id']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                results.add_test("Formato de Resposta", True, "Todos os campos obrigatórios presentes")
            else:
                results.add_test("Formato de Resposta", False, f"Campos ausentes: {missing_fields}")
        else:
            results.add_test("Formato de Resposta", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Formato de Resposta", False, f"Erro: {str(e)}")

def test_encoding_support(results):
    """Teste 5: Suporte a caracteres especiais e encoding UTF-8"""
    ticket_data = {
        "title": "Teste Acentuação: áéíóú àèìòù âêîôû ãõ ç ñ ü",
        "description": "Descrição com caracteres especiais: ®©™€£¥§¶•‰‡†‹›""''—–…",
        "category": "SOFTWARE",
        "impact": "BAIXO",
        "location": "São Paulo - Prédio Açaí",
        "contact_phone": "(11) 99999-9999"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/create-ticket-complete",
            headers=HEADERS,
            json=ticket_data,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('sucesso'):
                results.add_test("Suporte a Encoding UTF-8", True, "Caracteres especiais processados corretamente")
            else:
                results.add_test("Suporte a Encoding UTF-8", False, f"Falha: {data.get('erro')}")
        else:
            results.add_test("Suporte a Encoding UTF-8", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.add_test("Suporte a Encoding UTF-8", False, f"Erro: {str(e)}")

def test_impact_mapping(results):
    """Teste 6: Validação do mapeamento de impacto"""
    impact_tests = [
        ("ALTO", "Impacto Alto"),
        ("MEDIO", "Impacto Médio"), 
        ("BAIXO", "Impacto Baixo"),
        ("CRITICO", "Impacto Crítico")
    ]
    
    for impact, description in impact_tests:
        ticket_data = {
            "title": f"Teste {description}",
            "description": f"Validando mapeamento de {description}",
            "category": "HARDWARE",
            "impact": impact,
            "location": "Teste",
            "contact_phone": "(51) 77777-7777"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/create-ticket-complete",
                headers=HEADERS,
                json=ticket_data,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('sucesso'):
                    results.add_test(f"Mapeamento {description}", True, f"Impacto '{impact}' processado corretamente")
                else:
                    results.add_test(f"Mapeamento {description}", False, f"Falha: {data.get('erro')}")
            else:
                results.add_test(f"Mapeamento {description}", False, f"Status code: {response.status_code}")
        except Exception as e:
            results.add_test(f"Mapeamento {description}", False, f"Erro: {str(e)}")

def test_concurrent_requests(results):
    """Teste 7: Teste de requisições concorrentes"""
    import threading
    import queue
    
    def create_ticket(q, thread_id):
        ticket_data = {
            "title": f"Teste Concorrente #{thread_id}",
            "description": f"Ticket criado pela thread {thread_id}",
            "category": "SOFTWARE",
            "impact": "MEDIO",
            "location": f"Local Thread {thread_id}",
            "contact_phone": f"(51) 9999-{thread_id:04d}"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/create-ticket-complete",
                headers=HEADERS,
                json=ticket_data,
                timeout=30
            )
            q.put((thread_id, response.status_code == 201, response.json() if response.status_code == 201 else None))
        except Exception as e:
            q.put((thread_id, False, str(e)))
    
    # Criar 5 threads para teste concorrente
    threads = []
    result_queue = queue.Queue()
    
    for i in range(5):
        thread = threading.Thread(target=create_ticket, args=(result_queue, i+1))
        threads.append(thread)
        thread.start()
    
    # Aguardar todas as threads
    for thread in threads:
        thread.join()
    
    # Coletar resultados
    successful = 0
    failed = 0
    
    while not result_queue.empty():
        thread_id, success, data = result_queue.get()
        if success:
            successful += 1
        else:
            failed += 1
    
    if successful == 5:
        results.add_test("Requisições Concorrentes", True, f"Todas as 5 requisições foram processadas com sucesso")
    else:
        results.add_test("Requisições Concorrentes", False, f"Sucesso: {successful}, Falhas: {failed}")

def test_lookup_endpoint_validation(results):
    """Teste 8: Validação do endpoint de lookup sem parâmetro 'email'"""
    try:
        response = requests.get(f"{BASE_URL}/api/glpi-user-by-email", timeout=10)
        if response.status_code == 400:
            data = response.json()
            if not data.get('sucesso') and 'email' in (data.get('error','') + data.get('erro','')):
                results.add_test("Lookup sem email", True, "Validação de parâmetro funcionou")
            else:
                results.add_test("Lookup sem email", False, f"Resposta inesperada: {data}")
        else:
            results.add_test("Lookup sem email", False, f"Status inesperado: {response.status_code}")
    except Exception as e:
        results.add_test("Lookup sem email", False, f"Erro: {str(e)}")

def main():
    print("Iniciando testes automatizados da API...")
    print(f"URL Base: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    results = TestResults()
    
    # Executar todos os testes
    print("1. Testando Health Check...")
    test_health_check(results)
    
    print("2. Testando validação de campos obrigatórios...")
    test_missing_fields(results)
    
    print("3. Testando criação de ticket válido...")
    ticket_id, trace_id = test_valid_ticket_creation(results)
    
    print("4. Testando formato de resposta...")
    test_response_format(results)
    
    print("5. Testando suporte a encoding UTF-8...")
    test_encoding_support(results)
    
    print("6. Testando mapeamento de impacto...")
    test_impact_mapping(results)
    
    print("7. Testando requisições concorrentes...")
    test_concurrent_requests(results)
    
    print("8. Testando endpoint de lookup de usuário...")
    test_lookup_endpoint_validation(results)
    
    # Imprimir resumo
    results.print_summary()
    
    # Salvar resultados em arquivo
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(results.tests),
                'passed': results.passed,
                'failed': results.failed,
                'success_rate': results.passed/len(results.tests)*100
            },
            'tests': results.tests
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em: test_results.json")
    
    # Retornar código de saída baseado nos resultados
    return 0 if results.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())