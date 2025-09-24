from datetime import datetime

class ChatbotMessage:
    """
    Representa un mensaje en la conversación del chatbot.
    """

    def __init__(self, user_message: str, bot_response: str, emotion_type: str = "Neutra", timestamp: datetime = None, message_id: str = None):
        """
        Inicializa un mensaje del chatbot.
        :param user_message: Mensaje del usuario.
        :param bot_response: Respuesta del chatbot.
        :param emotion_type: Tipo de emoción detectada (Positiva, Negativa, Neutra).
        :param timestamp: Momento en que ocurrió la conversación.
        :param message_id: ID único del mensaje en Firestore.
        """
        self.user_message = user_message
        self.bot_response = bot_response
        self.emotion_type = emotion_type
        self.timestamp = timestamp or datetime.now()
        self.message_id = message_id
        
    def __str__(self):
        """
        Devuelve una representación en string del mensaje para usar en prompts.
        """
        return f"Usuario: {self.user_message}\nAsistente: {self.bot_response}"
    
    def __repr__(self):
        """
        Devuelve una representación para debugging.
        """
        return f"ChatbotMessage(user='{self.user_message[:50]}...', bot='{self.bot_response[:50]}...', emotion='{self.emotion_type}', timestamp={self.timestamp})"


    def to_dict(self) -> dict:
        """
        Convierte el mensaje a un diccionario para su almacenamiento o serialización.
        :return: Diccionario con la estructura del mensaje.
        """
        return {
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "emotion_type": self.emotion_type,
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: dict, message_id: str = None):
        """
        Crea un objeto `ChatbotMessage` desde un diccionario.
        :param data: Diccionario con la estructura del mensaje.
        :param message_id: ID del documento en Firestore.
        :return: Instancia de `ChatbotMessage`.
        """
        return ChatbotMessage(
            user_message=data.get("user_message", ""),
            bot_response=data.get("bot_response", ""),
            emotion_type=data.get("emotion_type", "Neutra"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
            message_id=message_id
        )
