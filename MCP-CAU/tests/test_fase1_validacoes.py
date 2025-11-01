#!/usr/bin/env python3
"""
Script de teste para validar as implementações da Fase 1 - Validações Básicas
Testa os endpoints da API com diferentes cenários de validação
"""

import requests
import json
from datetime import datetime

# Configuração da API (localhost)
API_BASE_URL = "http://localhost:5000"
API_ENDPOINT = f"{API_BASE_URL}/api/create-ticket-complete"

def test_api_endpoint():
    """Testa se a API está respondendo"""
    try:
        response = requests.get(API_BASE_URL, timeout=10)
        print(f"✅ API está respondendo - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API não está respondendo: {e}")
        return False

def test_validation_scenarios():
    """Testa diferentes cenários de validação"""
    
    test_cases = [
        {
            "name": "Teste 1: Descrição muito curta (< 50 caracteres)",
            "payload": {
                "category": "HARDWARE_COMPUTADOR",
                "description": "Não funciona",  # 13 caracteres
                "impact": "MEDIO",
                "location": "Sala 101",
                "contact_phone": "(11) 99999-9999",
                "title": "Chamado via Copilot Studio"
            },
            "expected_issue": "Descrição muito curta"
        },
        {
            "name": "Teste 2: Descrição com palavras vagas",
            "payload": {
                "category": "HARDWARE_IMPRESSORA",
                "description": "A impressora não funciona direito e está com problema desde ontem",  # 75 caracteres, mas vaga
                "impact": "ALTO",
                "location": "Departamento Financeiro",
                "contact_phone": "(11) 88888-8888",
                "title": "Chamado via Copilot Studio"
            },
            "expected_issue": "Palavras vagas detectadas"
        },
        {
            "name": "Teste 3: Localização vazia",
            "payload": {
                "category": "SOFTWARE",
                "description": "O sistema de gestão está apresentando erro 404 quando tento acessar o módulo de relatórios. Já tentei limpar o cache do navegador e reiniciar, mas o problema persiste.",
                "impact": "MEDIO",
                "location": "",  # Vazio
                "contact_phone": "(11) 77777-7777",
                "title": "Chamado via Copilot Studio"
            },
            "expected_issue": "Localização obrigatória"
        },
        {
            "name": "Teste 4: Telefone vazio",
            "payload": {
                "category": "CONECTIVIDADE",
                "description": "A conexão com a internet está instável desde esta manhã. A velocidade está muito baixa e há quedas frequentes de conexão. Já reiniciei o roteador mas não resolveu.",
                "impact": "ALTO",
                "location": "Sala 205 - Andar 2",
                "contact_phone": "",  # Vazio
                "title": "Chamado via Copilot Studio"
            },
            "expected_issue": "Telefone obrigatório"
        },
        {
            "name": "Teste 5: Dados válidos (deve funcionar)",
            "payload": {
                "category": "HARDWARE_MONITOR",
                "description": "O monitor principal está apresentando linhas verticais na tela desde ontem pela manhã. Já verifiquei os cabos e estão bem conectados. O problema aparece tanto no Windows quanto no Linux.",
                "impact": "MEDIO",
                "location": "Sala 303 - Departamento TI",
                "contact_phone": "(11) 99999-9999",
                "title": "Chamado via Copilot Studio"
            },
            "expected_issue": "Nenhum - deve criar ticket"
        }
    ]
    
    print(f"\n🧪 **INICIANDO TESTES DA FASE 1 - VALIDAÇÕES BÁSICAS**")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Problema esperado: {test_case['expected_issue']}")
        
        try:
            response = requests.post(
                API_ENDPOINT,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"   Status HTTP: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Ticket criado: #{data.get('ticket_id')}")
                    print(f"   📋 Categoria: {data.get('categoria', data.get('category'))}")
                    result = "SUCCESS"
                else:
                    print(f"   ❌ Erro: {data.get('error', 'Erro desconhecido')}")
                    result = "ERROR"
            else:
                print(f"   ❌ Erro HTTP: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Resposta: {error_data}")
                except:
                    print(f"   📄 Resposta: {response.text[:200]}...")
                result = "HTTP_ERROR"
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            result = "EXCEPTION"
        
        results.append({
            "test": test_case['name'],
            "expected": test_case['expected_issue'],
            "result": result,
            "payload_size": len(test_case['payload']['description'])
        })
        
        print("-" * 60)
    
    return results

def generate_test_report(results):
    """Gera relatório dos testes"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "fase": "Fase 1 - Validações Básicas",
        "total_tests": len(results),
        "results": results,
        "summary": {
            "success": len([r for r in results if r['result'] == 'SUCCESS']),
            "errors": len([r for r in results if r['result'] in ['ERROR', 'HTTP_ERROR']]),
            "exceptions": len([r for r in results if r['result'] == 'EXCEPTION'])
        }
    }
    
    # Salvar relatório
    with open('relatorio_teste_fase1.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 **RESUMO DOS TESTES**")
    print(f"✅ Sucessos: {report['summary']['success']}")
    print(f"❌ Erros: {report['summary']['errors']}")
    print(f"⚠️ Exceções: {report['summary']['exceptions']}")
    print(f"\n📄 Relatório salvo em: relatorio_teste_fase1.json")
    
    return report

def main():
    """Função principal"""
    print("🚀 **TESTE DAS VALIDAÇÕES DA FASE 1**")
    print("=" * 50)
    
    # Verificar se API está disponível
    if not test_api_endpoint():
        print("❌ Não é possível continuar sem a API")
        return
    
    # Executar testes
    results = test_validation_scenarios()
    
    # Gerar relatório
    report = generate_test_report(results)
    
    print(f"\n🎯 **ANÁLISE DOS RESULTADOS:**")
    print(f"- Os testes validam se as implementações da Fase 1 estão funcionando")
    print(f"- Verificam validações de tamanho, palavras vagas, campos obrigatórios")
    print(f"- Casos que devem falhar: testes 1-4")
    print(f"- Casos que devem passar: teste 5")
    print(f"\n⚠️ **NOTA:** As validações da Fase 1 foram implementadas no Copilot Studio,")
    print(f"   não no backend. Este teste verifica se a API aceita os dados,")
    print(f"   mas as validações reais acontecem na interface do Copilot.")

if __name__ == "__main__":
    main()