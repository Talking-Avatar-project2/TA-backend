from datetime import datetime

class ChatbotMessage:
    """
    Representa un mensaje en la conversación del chatbot.
    """

    def __init__(self, user_message: str, bot_response: str, timestamp: datetime = None):
        """
        Inicializa un mensaje del chatbot.
        :param user_message: Mensaje del usuario.
        :param bot_response: Respuesta del chatbot.
        :param timestamp: Momento en que ocurrió la conversación.
        """
        self.user_message = user_message
        self.bot_response = bot_response
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        """
        Convierte el mensaje a un diccionario para su almacenamiento o serialización.
        :return: Diccionario con la estructura del mensaje.
        """
        return {
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: dict):
        """
        Crea un objeto `ChatbotMessage` desde un diccionario.
        :param data: Diccionario con la estructura del mensaje.
        :return: Instancia de `ChatbotMessage`.
        """
        return ChatbotMessage(
            user_message=data.get("user_message", ""),
            bot_response=data.get("bot_response", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None
        )
