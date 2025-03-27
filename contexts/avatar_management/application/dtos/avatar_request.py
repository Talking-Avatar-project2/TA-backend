class AvatarRequestDTO:
    """
    DTO para representar la solicitud de animación del avatar.
    """
    def __init__(self, emotion: str):
        self.emotion = emotion

    def to_dict(self) -> dict:
        """
        Convierte el objeto en un diccionario.
        """
        return {"emotion": self.emotion}
