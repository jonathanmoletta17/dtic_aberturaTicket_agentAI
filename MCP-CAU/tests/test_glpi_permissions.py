#!/usr/bin/env python3
"""
Script para testar permissões e configurações do GLPI
"""

import os
import requests
import json
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

def testar_permissoes():
    """Testa diferentes aspectos das permissões do GLPI"""
    print("🔍 TESTANDO PERMISSÕES DO GLPI")
    print("=" * 50)
    
    headers = autenticar_glpi()
    
    # 1. Testar informações do usuário atual
    print("\n1. 👤 Informações do usuário atual:")
    try:
        response = requests.get(f"{GLPI_URL}/getMyProfiles", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            profiles = response.json()
            print(f"   Perfis: {json.dumps(profiles, indent=2, ensure_ascii=False)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")
    
    # 2. Testar entidades disponíveis
    print("\n2. 🏢 Entidades disponíveis:")
    try:
        response = requests.get(f"{GLPI_URL}/Entity", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            entities = response.json()
            print(f"   Entidades: {json.dumps(entities, indent=2, ensure_ascii=False)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")
    
    # 3. Testar permissões específicas
    print("\n3. 🔐 Testando permissões específicas:")
    
    # Testar leitura de tickets
    try:
        response = requests.get(f"{GLPI_URL}/Ticket?range=0-1", headers=headers, timeout=10)
        print(f"   Leitura de tickets - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na leitura: {str(e)}")
    
    # 4. Testar diferentes payloads para criação
    print("\n4. 🎯 Testando criação com diferentes configurações:")
    
    # Payload mínimo
    payload_minimo = {
        "input": {
            "name": "Teste Mínimo",
            "content": "Conteúdo de teste"
        }
    }
    
    print("\n   4.1. Payload mínimo:")
    try:
        response = requests.post(f"{GLPI_URL}/Ticket", headers=headers, json=payload_minimo, timeout=10)
        print(f"        Status: {response.status_code}")
        print(f"        Resposta: {response.text}")
    except Exception as e:
        print(f"        Erro: {str(e)}")
    
    # Payload com entidade diferente
    payload_entidade = {
        "input": {
            "name": "Teste com Entidade",
            "content": "Conteúdo de teste",
            "entities_id": 1
        }
    }
    
    print("\n   4.2. Payload com entities_id = 1:")
    try:
        response = requests.post(f"{GLPI_URL}/Ticket", headers=headers, json=payload_entidade, timeout=10)
        print(f"        Status: {response.status_code}")
        print(f"        Resposta: {response.text}")
    except Exception as e:
        print(f"        Erro: {str(e)}")
    
    # 5. Verificar informações da sessão
    print("\n5. 📋 Informações da sessão:")
    try:
        response = requests.get(f"{GLPI_URL}/getFullSession", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session = response.json()
            print(f"   Sessão: {json.dumps(session, indent=2, ensure_ascii=False)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")

def main():
    print("🚀 INICIANDO TESTE DE PERMISSÕES GLPI")
    print(f"📍 URL: {GLPI_URL}")
    print(f"🔑 App Token: {GLPI_APP_TOKEN[:10]}...")
    print(f"👤 User Token: {GLPI_USER_TOKEN[:10]}...")
    
    testar_permissoes()
    
    print("\n" + "=" * 50)
    print("✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    main()