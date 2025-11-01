#!/usr/bin/env python3
"""
Script para testar acesso a diferentes entidades no GLPI
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GLPI_URL = os.getenv("GLPI_URL")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

def autenticar_glpi():
    """Autentica no GLPI e retorna headers com session token"""
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
        print(f"Erro na autenticação GLPI: {str(e)}")
        raise

def testar_entidades():
    """Testa criação de tickets em diferentes entidades"""
    print("🔍 TESTANDO ACESSO A DIFERENTES ENTIDADES")
    print("=" * 50)
    
    headers = autenticar_glpi()
    
    # Testa entidades 0, 1, 2
    entidades_teste = [0, 1, 2]
    
    for entity_id in entidades_teste:
        print(f"\n🏢 Testando entidade {entity_id}:")
        
        payload = {
            "input": {
                "name": f"Teste Entidade {entity_id}",
                "content": f"Teste de criação de ticket na entidade {entity_id}",
                "type": 1,
                "urgency": 3,
                "impact": 3,
                "priority": 3,
                "status": 2,
                "entities_id": entity_id
            }
        }
        
        try:
            response = requests.post(
                f"{GLPI_URL}/Ticket",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ Sucesso! Ticket ID: {result.get('id')}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)}")

if __name__ == "__main__":
    testar_entidades()