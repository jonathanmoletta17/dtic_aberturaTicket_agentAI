#!/usr/bin/env python3
"""
Teste do Fluxo Completo do Copilot Studio - Fase 1
==================================================

Este script simula o fluxo completo de interação do usuário com o Copilot Studio,
testando as validações implementadas na Fase 1:

1. Validação de tamanho mínimo da descrição (50 caracteres)
2. Detecção de palavras vagas na descrição
3. Validação de campos obrigatórios (telefone, localização)
4. Criação bem-sucedida de tickets com dados válidos

O teste simula as etapas que o Copilot Studio seguiria:
- Coleta de dados do usuário
- Aplicação das validações
- Chamada para a API apenas se os dados passarem nas validações
"""

import requests
import json
import datetime
from typing import Dict, List, Tuple, Any

# Configuração da API
API_BASE_URL = "http://localhost:5000"
API_ENDPOINT = f"{API_BASE_URL}/api/create-ticket-complete"

class CopilotStudioSimulator:
    """Simula o comportamento do Copilot Studio com as validações da Fase 1"""
    
    def __init__(self):
        self.vague_words = ['problema', 'erro', 'não funciona', 'quebrado', 'ruim', 'lento', 'travando', 'bug']
        
    def validate_description_length(self, description: str) -> Tuple[bool, str]:
        """Valida se a descrição tem pelo menos 50 caracteres"""
        if not description or len(description.strip()) < 50:
            return False, "❌ Descrição muito curta. Forneça uma descrição detalhada com pelo menos 50 caracteres."
        return True, "✅ Descrição tem tamanho adequado"
        
    def validate_vague_words(self, description: str) -> Tuple[bool, str]:
        """Detecta palavras vagas na descrição"""
        if not description:
            return True, "✅ Descrição vazia - validação não aplicável"
            
        description_lower = description.lower()
        found_vague_words = [word for word in self.vague_words if word in description_lower]
        
        if found_vague_words and len(description.strip()) < 100:
            return False, f"❌ Descrição contém palavras vagas: {', '.join(found_vague_words)}. Seja mais específico."
        return True, "✅ Descrição é específica e detalhada"
        
    def validate_location(self, location: str) -> Tuple[bool, str]:
        """Valida se a localização foi fornecida"""
        if not location or len(location.strip()) < 3:
            return False, "❌ Localização é obrigatória e deve ter pelo menos 3 caracteres."
        return True, "✅ Localização fornecida"
        
    def validate_phone(self, phone: str) -> Tuple[bool, str]:
        """Valida se o telefone foi fornecido"""
        if not phone or len(phone.strip()) < 8:
            return False, "❌ Telefone é obrigatório e deve ter pelo menos 8 dígitos."
        return True, "✅ Telefone fornecido"
        
    def simulate_copilot_flow(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula o fluxo completo do Copilot Studio"""
        result = {
            'test_name': test_data['name'],
            'expected_outcome': test_data['expected'],
            'validations': [],
            'copilot_decision': None,
            'api_call_made': False,
            'api_response': None,
            'final_result': None
        }
        
        # Aplicar validações do Copilot Studio
        description = test_data['payload'].get('description', '')
        location = test_data['payload'].get('location', '')
        phone = test_data['payload'].get('contact_phone', '')
        
        # Validação 1: Tamanho da descrição
        valid_desc, desc_msg = self.validate_description_length(description)
        result['validations'].append({'validation': 'description_length', 'passed': valid_desc, 'message': desc_msg})
        
        # Validação 2: Palavras vagas
        valid_vague, vague_msg = self.validate_vague_words(description)
        result['validations'].append({'validation': 'vague_words', 'passed': valid_vague, 'message': vague_msg})
        
        # Validação 3: Localização
        valid_location, location_msg = self.validate_location(location)
        result['validations'].append({'validation': 'location', 'passed': valid_location, 'message': location_msg})
        
        # Validação 4: Telefone
        valid_phone, phone_msg = self.validate_phone(phone)
        result['validations'].append({'validation': 'phone', 'passed': valid_phone, 'message': phone_msg})
        
        # Decisão do Copilot Studio
        all_validations_passed = all(v['passed'] for v in result['validations'])
        
        if all_validations_passed:
            result['copilot_decision'] = 'PROCEED_TO_API'
            result['api_call_made'] = True
            
            # Fazer chamada para a API
            try:
                response = requests.post(API_ENDPOINT, json=test_data['payload'], timeout=10)
                result['api_response'] = {
                    'status_code': response.status_code,
                    'response_data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
                
                if response.status_code == 201:
                    result['final_result'] = 'SUCCESS'
                else:
                    result['final_result'] = 'API_ERROR'
                    
            except Exception as e:
                result['api_response'] = {'error': str(e)}
                result['final_result'] = 'EXCEPTION'
        else:
            result['copilot_decision'] = 'BLOCK_API_CALL'
            result['final_result'] = 'VALIDATION_FAILED'
            
        return result

def run_copilot_flow_tests():
    """Executa os testes do fluxo completo do Copilot Studio"""
    
    print("🤖 TESTE DO FLUXO COMPLETO DO COPILOT STUDIO - FASE 1")
    print("=" * 60)
    print()
    
    # Casos de teste
    test_cases = [
        {
            'name': 'Descrição muito curta',
            'expected': 'Deve ser bloqueado pelo Copilot Studio',
            'payload': {
                'title': 'Problema no PC',
                'description': 'Problema no PC',  # 14 caracteres - muito curto
                'category': 'HARDWARE_COMPUTADOR',
                'impact': 'MEDIO',
                'location': 'Sala 101',
                'contact_phone': '11999887766'
            }
        },
        {
            'name': 'Descrição com palavras vagas',
            'expected': 'Deve ser bloqueado pelo Copilot Studio',
            'payload': {
                'title': 'Computador com problema',
                'description': 'Meu computador está com problema e não funciona direito',  # 65 caracteres com palavras vagas
                'category': 'HARDWARE_COMPUTADOR',
                'impact': 'MEDIO',
                'location': 'Sala 102',
                'contact_phone': '11999887766'
            }
        },
        {
            'name': 'Localização vazia',
            'expected': 'Deve ser bloqueado pelo Copilot Studio',
            'payload': {
                'title': 'Problema de acesso ao sistema',
                'description': 'Estou enfrentando dificuldades para acessar o sistema de gestão de documentos. Quando tento fazer login, a página carrega mas não aceita minhas credenciais válidas.',
                'category': 'SOFTWARE_SISTEMA',
                'impact': 'ALTO',
                'location': '',  # Localização vazia
                'contact_phone': '11999887766'
            }
        },
        {
            'name': 'Telefone vazio',
            'expected': 'Deve ser bloqueado pelo Copilot Studio',
            'payload': {
                'title': 'Falhas no monitor',
                'description': 'O monitor do meu computador está apresentando falhas intermitentes na exibição. A tela fica piscando e às vezes fica completamente preta por alguns segundos.',
                'category': 'HARDWARE_MONITOR',
                'impact': 'MEDIO',
                'location': 'Sala 103',
                'contact_phone': ''  # Telefone vazio
            }
        },
        {
            'name': 'Dados válidos',
            'expected': 'Deve passar por todas as validações e criar ticket',
            'payload': {
                'title': 'Problema na impressora HP LaserJet',
                'description': 'Estou com dificuldades para imprimir documentos na impressora HP LaserJet localizada no segundo andar. O equipamento está ligado e conectado à rede, mas quando envio documentos para impressão, eles ficam na fila e não são processados. Já tentei reiniciar a impressora e verificar as conexões.',
                'category': 'HARDWARE_IMPRESSORA',
                'impact': 'BAIXO',
                'location': 'Segundo Andar - Sala 205',
                'contact_phone': '11987654321'
            }
        }
    ]
    
    simulator = CopilotStudioSimulator()
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Teste {i}: {test_case['name']}")
        print(f"   Expectativa: {test_case['expected']}")
        print()
        
        result = simulator.simulate_copilot_flow(test_case)
        results.append(result)
        
        # Exibir validações
        print("   📋 Validações do Copilot Studio:")
        for validation in result['validations']:
            status = "✅" if validation['passed'] else "❌"
            print(f"      {status} {validation['validation']}: {validation['message']}")
        
        print()
        print(f"   🤖 Decisão do Copilot: {result['copilot_decision']}")
        
        if result['api_call_made']:
            api_resp = result['api_response']
            print(f"   🌐 Chamada API: Status {api_resp['status_code']}")
            if api_resp['status_code'] == 201:
                ticket_id = api_resp['response_data'].get('ticket_id', 'N/A')
                print(f"   🎫 Ticket criado: #{ticket_id}")
        else:
            print("   🚫 API não foi chamada (bloqueado pelas validações)")
            
        print(f"   🎯 Resultado final: {result['final_result']}")
        print("-" * 60)
        print()
    
    # Resumo
    validation_blocks = sum(1 for r in results if r['final_result'] == 'VALIDATION_FAILED')
    api_successes = sum(1 for r in results if r['final_result'] == 'SUCCESS')
    api_errors = sum(1 for r in results if r['final_result'] == 'API_ERROR')
    exceptions = sum(1 for r in results if r['final_result'] == 'EXCEPTION')
    
    print("📊 RESUMO DOS TESTES DO FLUXO COPILOT STUDIO")
    print("=" * 50)
    print(f"🚫 Bloqueados pelas validações: {validation_blocks}")
    print(f"✅ Sucessos (tickets criados): {api_successes}")
    print(f"❌ Erros da API: {api_errors}")
    print(f"⚠️ Exceções: {exceptions}")
    print()
    
    # Salvar relatório
    report = {
        'timestamp': datetime.datetime.now().isoformat(),
        'test_type': 'Fluxo Completo Copilot Studio - Fase 1',
        'total_tests': len(test_cases),
        'results': results,
        'summary': {
            'validation_blocks': validation_blocks,
            'api_successes': api_successes,
            'api_errors': api_errors,
            'exceptions': exceptions
        }
    }
    
    with open('relatorio_fluxo_copilot_completo.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("📄 Relatório salvo em: relatorio_fluxo_copilot_completo.json")
    print()
    
    # Análise dos resultados
    print("🎯 ANÁLISE DOS RESULTADOS:")
    print("- Este teste simula o comportamento real do Copilot Studio")
    print("- Validações são aplicadas ANTES de chamar a API")
    print("- Casos inválidos são bloqueados pelo Copilot Studio")
    print("- Apenas dados válidos chegam à API")
    print()
    
    if validation_blocks == 4 and api_successes == 1:
        print("✅ TESTE PASSOU: Validações funcionando corretamente!")
        print("   - 4 casos inválidos foram bloqueados pelo Copilot Studio")
        print("   - 1 caso válido passou e criou ticket com sucesso")
    else:
        print("❌ TESTE FALHOU: Validações não estão funcionando como esperado")
        print("   - Verifique a implementação das validações no Copilot Studio")

if __name__ == "__main__":
    run_copilot_flow_tests()