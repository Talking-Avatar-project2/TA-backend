class AvatarResponseDTO:
    """
    DTO para representar la respuesta de animación del avatar.
    """
    def __init__(self, message: str):
        self.message = message

    def to_dict(self) -> dict:
        """
        Convierte el objeto en un diccionario.
        """
        return {"message": self.message}
