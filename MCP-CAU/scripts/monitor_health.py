#!/usr/bin/env python3
"""
Script de monitoramento de saúde do servidor GLPI Agent.
Verifica periodicamente se o servidor está respondendo e reinicia se necessário.
"""

import time
import requests
import subprocess
import logging
import sys
import os
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ServerMonitor:
    def __init__(self, server_url="http://localhost:5000", check_interval=30):
        self.server_url = server_url
        self.health_endpoint = f"{server_url}/api/health"
        self.check_interval = check_interval
        self.consecutive_failures = 0
        self.max_failures = 3
        self.server_process = None
        
    def check_health(self):
        """Verifica se o servidor está saudável."""
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('glpi_connection') == 'ok':
                    return True
            return False
        except Exception as e:
            logger.warning(f"Health check falhou: {e}")
            return False
    
    def start_server(self):
        """Inicia o servidor."""
        try:
            logger.info("Iniciando servidor...")
            self.server_process = subprocess.Popen([
                sys.executable, "run_server.py"
            ], cwd=os.getcwd())
            
            # Aguarda um pouco para o servidor inicializar
            time.sleep(5)
            
            # Verifica se o servidor iniciou corretamente
            if self.check_health():
                logger.info(f"Servidor iniciado com sucesso! PID: {self.server_process.pid}")
                return True
            else:
                logger.error("Servidor iniciou mas health check falhou")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self):
        """Para o servidor."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("Servidor parado")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.warning("Servidor forçadamente finalizado")
            except Exception as e:
                logger.error(f"Erro ao parar servidor: {e}")
    
    def restart_server(self):
        """Reinicia o servidor."""
        logger.info("Reiniciando servidor...")
        self.stop_server()
        time.sleep(2)
        return self.start_server()
    
    def monitor(self):
        """Loop principal de monitoramento."""
        logger.info("=== Iniciando Monitor de Saúde do Servidor GLPI ===")
        logger.info(f"URL: {self.server_url}")
        logger.info(f"Intervalo de verificação: {self.check_interval}s")
        logger.info(f"Máximo de falhas consecutivas: {self.max_failures}")
        
        # Inicia o servidor se não estiver rodando
        if not self.check_health():
            if not self.start_server():
                logger.error("Falha ao iniciar servidor. Encerrando monitor.")
                return
        
        try:
            while True:
                if self.check_health():
                    if self.consecutive_failures > 0:
                        logger.info("Servidor recuperado!")
                    self.consecutive_failures = 0
                    logger.info("[OK] Servidor saudavel")
                else:
                    self.consecutive_failures += 1
                    logger.warning(f"[ERRO] Health check falhou ({self.consecutive_failures}/{self.max_failures})")
                    
                    if self.consecutive_failures >= self.max_failures:
                        logger.error("Máximo de falhas atingido. Reiniciando servidor...")
                        if self.restart_server():
                            self.consecutive_failures = 0
                        else:
                            logger.error("Falha ao reiniciar servidor!")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no monitor: {e}")
        finally:
            self.stop_server()

def main():
    """Função principal."""
    monitor = ServerMonitor()
    monitor.monitor()

if __name__ == "__main__":
    main()