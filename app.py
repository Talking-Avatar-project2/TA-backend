# app.py (versión estable LiveAvatar 4.0)

import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS  # <-- NUEVO

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config
from contexts.recognition_management.application.controllers.facial_recognition_controller import facial_recognition_bp
from contexts.chatbot_management.application.controllers.chatbot_controller import chatbot_bp
from contexts.avatar_management.application.controllers.avatar_controller import avatar_bp
from shared.utils.error_handler import handle_errors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # <<<--- CORS PERMITIENDO LLAMADAS DESDE TU FRONTEND
    CORS(
        app,
        resources={r"/*": {"origins": "*"}}
        # si quieres más estricto:
        # resources={r"/*": {"origins": ["http://localhost:51392", "http://192.168.1.36:51392"]}}
    )

    app.register_blueprint(facial_recognition_bp, url_prefix="/recognition")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(avatar_bp, url_prefix="/avatar")

    app.register_error_handler(Exception, handle_errors)

    @app.get("/")
    def home():
        return {"message": "Backend Refactorizado + LiveAvatar 4.0 Activo"}, 200

    @app.get("/debug/env")
    def debug_env():
        return {
            "LIVEAVATAR_API_KEY": bool(Config.LIVEAVATAR_API_KEY),
            "LIVEAVATAR_API_URL": Config.LIVEAVATAR_API_URL,
        }

    return app


if __name__ == "__main__":
    app = create_app()

    print("")
    print("=======================================")
    print("   LIVEAVATAR DEBUG - VARIABLES ENV    ")
    print("=======================================")
    print("LIVEAVATAR_API_KEY:", bool(Config.LIVEAVATAR_API_KEY))
    print("LIVEAVATAR_API_URL:", Config.LIVEAVATAR_API_URL)
    print("=======================================")
    print("")

    app.run(host="0.0.0.0", port=5000, debug=True)
