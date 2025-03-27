class ChatbotResponseDTO:
    """
    DTO para representar la respuesta del chatbot.
    """

    def __init__(self, bot_response: str):
        self.bot_response = bot_response

    def to_dict(self) -> dict:
        """Convierte la respuesta en un diccionario serializable."""
        return {"bot_response": self.bot_response}
