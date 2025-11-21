# contexts/recognition_management/domain/repositories/emotion_repository_interface.py

from abc import ABC, abstractmethod
from typing import Dict

class EmotionRepositoryInterface(ABC):

    @abstractmethod
    def save_emotion_session(self, user_id: str, session_data: Dict) -> str:
        """
        Guarda una sesión de FER en Firestore y retorna el ID del documento.
        """
        pass

    @abstractmethod
    def get_emotion_sessions(self, user_id: str, limit: int = 10):
        """
        Obtiene las últimas sesiones FER guardadas.
        """
        pass
