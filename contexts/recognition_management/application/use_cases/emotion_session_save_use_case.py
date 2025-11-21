# contexts/recognition_management/application/use_cases/emotion_session_save_use_case.py

from datetime import datetime
from contexts.recognition_management.infrastructure.repositories.emotion_repository import EmotionRepository

class EmotionSessionSaveUseCase:

    @staticmethod
    def execute(user_id: str, stats: dict, dominant_emotion: str):
        """
        Guarda una sesión FER completa en Firestore.
        """

        payload = {
            "timestamp": datetime.utcnow(),
            "stats": stats,
            "dominant_emotion": dominant_emotion
        }

        repo = EmotionRepository()
        doc_id = repo.save_emotion_session(user_id, payload)

        return {"emotion_session_id": doc_id, "saved": True}
