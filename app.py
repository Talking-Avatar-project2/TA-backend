# app.py
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS  # <-- NUEVO

from config import Config
# from contexts.recognition_management.application.controllers.facial_recognition_controller import facial_recognition_bp  # Temporalmente deshabilitado
from contexts.chatbot_management.application.controllers.chatbot_controller import chatbot_bp
from contexts.avatar_management.application.controllers.avatar_controller import avatar_bp
from contexts.profile_management.application.controllers.profile_controller import profile_bp
from contexts.user_management.application.controllers.user_controller import user_bp
from contexts.recognition_management.application.controllers.facial_recognition_controller import facial_recognition_bp
from contexts.recognition_management.domain.services.fer_session_manager import FerSessionManager
from shared.utils.error_handler import handle_errors
from firebase_config import initialize_firebase
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def create_app():
    """Inicializa la aplicación Flask y registra los blueprints."""
    app = Flask(__name__)

    # Cargar configuración desde config.py
    app.config.from_object(Config)

    # Inicializar Firebase (si las credenciales están configuradas)
    try:
        initialize_firebase()
    except FileNotFoundError as e:
        app.logger.warning(f"Firebase no inicializado: {e}")
    except Exception as e:
        app.logger.warning(f"Error al inicializar Firebase: {e}")

    # Registrar controladores (blueprints) de cada contexto
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
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(user_bp, url_prefix="/auth")

    # Middleware para manejo de errores global
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

    # NEW: endpoint para verificar estado del FER
    @app.get("/recognition/status")
    def fer_status():
        return {"fer_running": FerSessionManager._running,
                "stats": FerSessionManager.get_stats()}, 200

    return app
"""
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

    #app.run(host="0.0.0.0", port=5000, debug=True)
"""
    app = create_app()
