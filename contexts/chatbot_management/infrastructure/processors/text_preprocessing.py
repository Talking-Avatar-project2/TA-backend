import re

class TextPreprocessing:
    """Procesador de texto para limpiar y normalizar mensajes del usuario."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpia el texto eliminando caracteres especiales y espacios innecesarios.
        :param text: Mensaje de entrada del usuario.
        :return: Texto limpio y normalizado.
        """
        text = text.lower().strip()  # Convertir a minúsculas y eliminar espacios en los extremos
        text = re.sub(r"[^a-zA-Z0-9áéíóúüñ,.!? ]", "", text)  # Permitir solo caracteres válidos
        return text
