from app_core import create_app
from flask import jsonify

app = create_app()


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Agente Copilot Studio - GLPI",
        "status": "ativo",
        "version": "2.0",
        "endpoints": {
            "health": "/api/health",
            "create_ticket": "/api/create-ticket-complete",
            "user_by_email": "/api/glpi-user-by-email"
        }
    })


if __name__ == "__main__":
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
