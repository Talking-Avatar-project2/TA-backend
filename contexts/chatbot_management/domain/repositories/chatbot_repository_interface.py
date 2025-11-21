from abc import ABC, abstractmethod
from typing import List
from contexts.chatbot_management.domain.entities.chatbot_message import ChatbotMessage

class ChatbotRepositoryInterface(ABC):
    """Interfaz para el repositorio del chatbot."""

    @abstractmethod
    def save_message(self, user_message: str, bot_response: str):
        """Guarda un mensaje en el historial."""
        pass

    @abstractmethod
    def get_conversation_history(self, limit: int) -> List[ChatbotMessage]:
        """Obtiene el historial de conversaciones."""
        pass
