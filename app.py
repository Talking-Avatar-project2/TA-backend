# app.py
import os
import threading
import time
import numpy as np
import cv2
import pygame
from flask import Flask
from config import Config
from contexts.recognition_management.application.controllers.facial_recognition_controller import facial_recognition_bp
from contexts.chatbot_management.application.controllers.chatbot_controller import chatbot_bp
from contexts.avatar_management.application.controllers.avatar_controller import avatar_bp
from shared.utils.error_handler import handle_errors

# Callbacks del detector -> Avatar
from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService
from contexts.recognition_management.infrastructure.processors.realtime_emotion_detector import run_realtime_detector

# --- Display en un solo proceso ---
from contexts.avatar_management.infrastructure.display.avatar_display_service import AvatarDisplayService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(facial_recognition_bp, url_prefix="/recognition")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(avatar_bp, url_prefix="/avatar")
    app.register_error_handler(Exception, handle_errors)

    @app.get("/")
    def home():
        return {"message": "Backend Refactorizado Activo"}, 200

    return app

# -------- Orquestación en runtime --------
def _on_emotion(emotion: str, confidence: float) -> None:
    try:
        # compat: ya no cambia la boca; puedes usarlo para micro-poses si luego quieres
        AvatarAnimationService.generate_animation(emotion)
    except Exception as e:
        print("[ERROR] generate_animation falló:", e, flush=True)

def _thread_recognition():
    run_realtime_detector(
        on_emotion=_on_emotion,
        # on_landmarks desactivado en V3.0:
        # on_landmarks=_on_landmarks,
        camera_size=(424, 240),
        fer_every_n_frames=1,
        show_camera_window=False,
        verbose=True,
    )

if __name__ == "__main__":
    AvatarAnimationService.initialize()     # init renderer atlas
    AvatarDisplayService.initialize()       # crea ventana pygame

    th_fer = threading.Thread(target=_thread_recognition, daemon=True)
    th_fer.start()
    print("[APP] Hilo de reconocimiento lanzado (FER)")

    flask_app = create_app()
    def _run_flask():
        flask_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    th_flask = threading.Thread(target=_run_flask, daemon=True)
    th_flask.start()
    print("[APP] Flask lanzado en hilo aparte")

    # Bucle principal: solo bombea eventos/refresco
    while getattr(AvatarDisplayService, "_running", True):
        AvatarDisplayService.pump()
        time.sleep(0.01)
