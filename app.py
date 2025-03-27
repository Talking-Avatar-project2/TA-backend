# app.py
from flask import Flask
from config import Config
from contexts.recognition_management.application.controllers.facial_recognition_controller import facial_recognition_bp
from contexts.chatbot_management.application.controllers.chatbot_controller import chatbot_bp
from contexts.avatar_management.application.controllers.avatar_controller import avatar_bp
from shared.utils.error_handler import handle_errors

def create_app():
    """Inicializa la aplicación Flask y registra los blueprints."""
    app = Flask(__name__)

    # Cargar configuración desde config.py
    app.config.from_object(Config)

    # Registrar controladores (blueprints) de cada contexto
    app.register_blueprint(facial_recognition_bp, url_prefix="/recognition")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(avatar_bp, url_prefix="/avatar")

    # Middleware para manejo de errores global
    app.register_error_handler(Exception, handle_errors)

    @app.route("/", methods=["GET"])
    def home():
        return {"message": "Backend Refactorizado Activo 🚀"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
