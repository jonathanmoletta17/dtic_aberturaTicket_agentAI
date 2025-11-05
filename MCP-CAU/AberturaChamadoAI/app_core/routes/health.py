# -*- coding: utf-8 -*-
import uuid
from flask import Blueprint, jsonify
from ..config import load_settings
from ..services.glpi import autenticar_glpi


health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health_check():
    try:
        settings = load_settings()
        config_ok = all([settings.glpi_url, settings.glpi_app_token, settings.glpi_user_token])
        status = {
            "status": "ok" if config_ok else "error",
            "glpi_configured": config_ok,
            "timestamp": str(uuid.uuid4()),
        }
        if config_ok:
            try:
                autenticar_glpi()
                status["glpi_connection"] = "ok"
            except Exception as e:
                status["glpi_connection"] = "error"
                status["glpi_error"] = str(e)
                status["status"] = "warning"
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


