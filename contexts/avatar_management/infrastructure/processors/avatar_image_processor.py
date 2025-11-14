#contexts/avatar_management/infrastructure/processors/avatar_image_processor.py
import os
import cv2
import numpy as np

class AvatarImageProcessor:
    """
    Procesador de imagen único para el avatar final.
    Carga la imagen neutral procesada y sus landmarks almacenados.
    """
    _base_dir = os.path.join("images", "avatar_final")
    _image_path = os.path.join(_base_dir, "neutral_processed.png")
    _landmarks_path = os.path.join(_base_dir, "neutral_landmarks.npy")

    _cached_image = None
    _cached_landmarks = None

    @staticmethod
    def load_avatar_image():
        """
        Carga la imagen base del avatar procesado (sin overlay).
        :return: np.ndarray (BGR)
        """
        if AvatarImageProcessor._cached_image is not None:
            return AvatarImageProcessor._cached_image

        if not os.path.exists(AvatarImageProcessor._image_path):
            raise FileNotFoundError(f"No se encontró la imagen del avatar en: {AvatarImageProcessor._image_path}")

        img = cv2.imread(AvatarImageProcessor._image_path)
        if img is None:
            raise IOError(f"No se pudo leer la imagen del avatar: {AvatarImageProcessor._image_path}")

        AvatarImageProcessor._cached_image = img
        print(f"[INFO] Imagen base del avatar cargada desde: {AvatarImageProcessor._image_path}")
        return img

    @staticmethod
    def load_avatar_landmarks():
        """
        Carga los landmarks guardados del avatar.
        :return: np.ndarray de shape (468, 3)
        """
        if AvatarImageProcessor._cached_landmarks is not None:
            return AvatarImageProcessor._cached_landmarks

        if not os.path.exists(AvatarImageProcessor._landmarks_path):
            raise FileNotFoundError(f"No se encontró el archivo de landmarks en: {AvatarImageProcessor._landmarks_path}")

        lm = np.load(AvatarImageProcessor._landmarks_path)
        AvatarImageProcessor._cached_landmarks = lm
        print(f"[INFO] Landmarks del avatar cargados desde: {AvatarImageProcessor._landmarks_path}")
        return lm

    @staticmethod
    def get_avatar_data():
        """
        Devuelve una tupla (imagen, landmarks) lista para usar.
        """
        img = AvatarImageProcessor.load_avatar_image()
        lm = AvatarImageProcessor.load_avatar_landmarks()
        return img, lm
