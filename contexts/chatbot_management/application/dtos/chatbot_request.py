class ChatbotRequestDTO:
    """
    DTO para representar la solicitud de un mensaje al chatbot.
    """

    def __init__(self, user_message: str, user_id: str):
        if not user_message or len(user_message) < 2 or not user_id:
            raise ValueError("El mensaje no puede estar vacío o ser demasiado corto.")

        self.user_message = user_message
        self.user_id=user_id
