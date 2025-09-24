# shared/processors/real_time_emotion_detection.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import signal
import cv2
from fer import FER
from shared.utils.emotion_image_paths import IMAGE_PATHS
from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService

# Variables de control
current_emotion = "neutral"
stop_program = False

def detect_real_time_emotions():
    """Captura video en tiempo real y detecta emociones en cada fotograma."""
    global current_emotion, stop_program
    detector = FER(mtcnn=True)
    cap = cv2.VideoCapture(0)

    try:
        while not stop_program:
            ret, frame = cap.read()
            if not ret:
                break

            emotion, score = detector.top_emotion(frame)
            if emotion and emotion != current_emotion:
                print(f"Emotion detected: {emotion}, Confidence: {score * 100:.2f}%")
                current_emotion = emotion
                AvatarAnimationService.generate_animation(current_emotion)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        AvatarAnimationService.close_animation()  # ✅ Cierra la ventana del avatar correctamente


def signal_handler(sig, frame):
    """Manejador de señal para interrupciones."""
    global stop_program
    print("\nSeñal recibida. Deteniendo el reconocimiento en tiempo real...")
    stop_program = True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Captura Ctrl+C para salir
    detect_real_time_emotions()
