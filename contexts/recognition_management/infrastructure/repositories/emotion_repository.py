# contexts/recognition_management/infrastructure/repositories/emotion_repository.py

from typing import Dict, List
from contexts.recognition_management.domain.repositories.emotion_repository_interface import EmotionRepositoryInterface
from shared.infrastructure.firestore_client import FirestoreClient

class EmotionRepository(EmotionRepositoryInterface):

    _firestore_client = None

    @classmethod
    def _get_client(cls):
        if cls._firestore_client is None:
            cls._firestore_client = FirestoreClient()
        return cls._firestore_client

    def save_emotion_session(self, user_id: str, session_data: Dict) -> str:
        """
        Guarda la sesión FER en Firestore bajo users/{user_id}/emotions
        """
        try:
            client = self._get_client()
            doc_id = client.add_document(f"users/{user_id}/emotions", session_data)
            print(f"FER session saved with ID: {doc_id}")
            return doc_id
        except Exception as e:
            print(f"Error saving FER session to Firestore: {e}")
            raise e

    def get_emotion_sessions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Obtiene sesiones FER ordenadas por timestamp descendente.
        """
        try:
            client = self._get_client()
            docs = client.get_documents(
                f"users/{user_id}/emotions",
                order_by="timestamp",
                limit=limit
            )
            return docs
        except Exception as e:
            print(f"Error fetching FER sessions: {e}")
            return []
