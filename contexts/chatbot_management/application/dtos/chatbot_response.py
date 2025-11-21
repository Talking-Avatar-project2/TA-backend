class ChatbotResponseDTO:
    """
    DTO para representar la respuesta del chatbot.
    """

    def __init__(self, response: str):
        self.response = response

    def to_dict(self) -> dict:
        """Convierte la respuesta en un diccionario serializable."""
        return {"response": self.response}
