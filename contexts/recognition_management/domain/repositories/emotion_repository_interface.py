from contexts.recognition_management.domain.entities.emotion import Emotion
from typing import Optional, List, Tuple

class EmotionRepository:
    _stored_emotions: List[Emotion] = []
    _stored_landmarks: List[List[Tuple[float, float, float]]] = []

    def save_emotion(self, emotion: Emotion):
        """
        Guarda la emoción detectada en una lista local.
        En una versión futura, podría guardarse en una base de datos.
        """
        self._stored_emotions.append(emotion)
        print(f"Emoción guardada: {emotion.dict()}")

    def get_last_emotion(self) -> Optional[Emotion]:
        """
        Retorna la última emoción detectada.
        """
        if self._stored_emotions:
            return self._stored_emotions[-1]
        return None

    def save_landmarks(self, landmarks: List[Tuple[float, float, float]]):
        """
        Guarda los landmarks detectados por MediaPipe.
        """
        self._stored_landmarks.append(landmarks)
        print(f"Landmarks guardados: {len(landmarks)} puntos")

    def get_last_landmarks(self) -> Optional[List[Tuple[float, float, float]]]:
        """
        Retorna los últimos landmarks detectados.
        """
        if self._stored_landmarks:
            return self._stored_landmarks[-1]
        return None
