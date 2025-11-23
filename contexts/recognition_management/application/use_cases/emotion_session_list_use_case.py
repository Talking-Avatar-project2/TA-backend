# contexts/recognition_management/application/use_cases/emotion_session_list_use_case.py
from contexts.recognition_management.infrastructure.repositories.emotion_repository import EmotionRepository


class EmotionSessionListUseCase:
    @staticmethod
    def execute(user_id: str, limit: int = 10):
        """Obtiene las sesiones FER previas del usuario desde Firestore."""
        repo = EmotionRepository()
        return repo.get_emotion_sessions(user_id=user_id, limit=limit)
