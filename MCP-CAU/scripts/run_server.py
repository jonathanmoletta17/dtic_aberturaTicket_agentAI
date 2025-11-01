#!/usr/bin/env python3
"""
Script para executar o servidor Flask com configurações de produção.
Inclui tratamento de exceções, logging e configurações otimizadas.
"""

import os
import sys
import signal
import logging
from app import app

# Configuração de logging para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handler para sinais de interrupção."""
    logger.info('Recebido sinal de interrupção. Encerrando servidor...')
    sys.exit(0)

def main():
    """Função principal para executar o servidor."""
    try:
        # Registra handlers para sinais
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("=== Iniciando Servidor Flask - Agente GLPI ===")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Diretório: {os.getcwd()}")
        
        # Configurações de produção
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # Inicia o servidor
        logger.info("Servidor iniciando na porta 5000...")
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()