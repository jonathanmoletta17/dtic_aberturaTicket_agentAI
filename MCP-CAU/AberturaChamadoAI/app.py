from AberturaChamadoAI.app_core import create_app

app = create_app()

if __name__ == "__main__":
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
