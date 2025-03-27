import os
from shared.utils.emotion_image_paths import IMAGE_PATHS

class AvatarImageProcessor:
    @staticmethod
    def get_emotion_images(emotion: str) -> list:
        """
        Devuelve la lista de imágenes asociadas a una emoción.
        :param emotion: Emoción detectada.
        :return: Lista de rutas de imágenes.
        """
        return IMAGE_PATHS.get(emotion, IMAGE_PATHS["neutral"])
