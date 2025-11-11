# -*- coding: utf-8 -*-
import logging
from flask import Flask
from flask import jsonify
from .config import load_settings
from .logging_config import configure_logging
from .routes.health import health_bp
from .routes.tickets import tickets_bp
from .routes.auth import auth_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # Configurações básicas
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # Carrega settings (.env) e logging
    settings = load_settings()
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Aplicação iniciando com app factory")

    # Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(auth_bp)

    # Log de rotas registradas
    for rule in app.url_map.iter_rules():
        logging.getLogger(__name__).info(f"Rota registrada: {rule}")

    # Rota raiz padronizada para ambos entrypoints (run_server.py e app.py)
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "Agente Copilot Studio - GLPI",
            "status": "ativo",
            "version": "2.0",
            "endpoints": {
                "health": "/api/health",
                "routes": "/api/routes",
                "create_ticket": "/api/create-ticket-complete",
                "user_by_email": "/api/glpi-user-by-email",
                "authenticate_user": "/api/authenticate-user"
            }
        })

    return app


