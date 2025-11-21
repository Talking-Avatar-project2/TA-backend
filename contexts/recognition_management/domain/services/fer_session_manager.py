# contexts/recognition_management/domain/services/fer_session_manager.py

import threading
import time

from contexts.recognition_management.infrastructure.processors.realtime_emotion_detector import (
    run_realtime_detector,
    stop_global_detector      # <--- nuevo import
)

class FerSessionManager:
    _thread = None
    _running = False
    _emotion_stats = {
        "angry": 0,
        "disgust": 0,
        "fear": 0,
        "happy": 0,
        "sad": 0,
        "surprise": 0,
        "neutral": 0,
    }

    @classmethod
    def _on_emotion(cls, emotion: str, confidence: float):
        emotion = emotion.lower().strip()
        if emotion in cls._emotion_stats:
            cls._emotion_stats[emotion] += 1
        print(f"[FER] Detected: {emotion} | conf={confidence:.2f}")

    @classmethod
    def _reset_stats(cls):
        for k in cls._emotion_stats.keys():
            cls._emotion_stats[k] = 0

    @classmethod
    def get_stats(cls):
        return dict(cls._emotion_stats)

    @classmethod
    def _run_detector(cls):
        print("[FER] Hilo FER iniciado")

        try:
            run_realtime_detector(
                on_emotion=cls._on_emotion,
                on_landmarks=None,
                camera_size=(424, 240),
                fer_every_n_frames=1,
                show_camera_window=False,
                verbose=True,
                # NUEVO: callback para saber si debe parar
                stop_condition=lambda: not cls._running
            )
        except Exception as e:
            print(f"[FER] Error en detector: {e}")

        print("[FER] Detector terminado")

    @classmethod
    def start(cls):
        if cls._running:
            print("[FER] Ya estaba corriendo")
            return

        cls._running = True
        cls._reset_stats()

        cls._thread = threading.Thread(target=cls._run_detector, daemon=True)
        cls._thread.start()

        print("===== FER STARTED =====")

    @classmethod
    def stop(cls):
        if not cls._running:
            print("[FER] Stop solicitado, pero no estaba corriendo")
            return

        print("===== FER STOP SIGNAL SENT =====")

        cls._running = False
        stop_global_detector()      # <--- detiene el loop en realtime_emotion_detector

        time.sleep(0.3)

        print("[FER] Finalizado correctamente")

        return cls.get_stats()
