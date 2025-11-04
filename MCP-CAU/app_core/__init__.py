# -*- coding: utf-8 -*-
import logging
from flask import Flask
from .config import load_settings
from .logging_config import configure_logging
from .routes.health import health_bp
from .routes.tickets import tickets_bp


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

    return app


