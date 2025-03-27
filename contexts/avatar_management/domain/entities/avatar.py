class Avatar:
    """
    Representa el avatar y sus características.
    """
    def __init__(self, emotion: str):
        self.emotion = emotion

    def to_dict(self) -> dict:
        """
        Convierte el objeto Avatar a un diccionario.
        """
        return {"emotion": self.emotion}
