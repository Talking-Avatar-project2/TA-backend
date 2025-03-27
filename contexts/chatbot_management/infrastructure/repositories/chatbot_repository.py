from contexts.chatbot_management.domain.repositories.chatbot_repository_interface import ChatbotRepositoryInterface
from contexts.chatbot_management.domain.entities.chatbot_message import ChatbotMessage

class ChatbotRepository(ChatbotRepositoryInterface):
    """Implementación en memoria del repositorio del chatbot."""

    _conversation_history = []  # Simulación de almacenamiento en memoria

    @staticmethod
    def save_message(user_message: str, bot_response: str):
        """Guarda el mensaje en el historial."""
        message = ChatbotMessage(user_message, bot_response)
        ChatbotRepository._conversation_history.append(message)

    @staticmethod
    def get_conversation_history(limit: int = 10):
        """Obtiene los últimos mensajes en la conversación."""
        return ChatbotRepository._conversation_history[-limit:]
