import cv2
import os
from contexts.avatar_management.infrastructure.processors.avatar_image_processor import AvatarImageProcessor

class AvatarAnimationService:
    _window_name = "Avatar Animation"
    _current_emotion = None  # Mantener la emoción actual
    _is_window_open = False   # Controlar si la ventana está abierta

    @staticmethod
    def generate_animation(emotion: str):
        """
        Muestra continuamente la animación del avatar basada en la emoción detectada.
        """
        if emotion == AvatarAnimationService._current_emotion:
            return  # No hacer nada si la emoción no ha cambiado

        AvatarAnimationService._current_emotion = emotion
        image_folder = "data/processed_avatars"
        selected_images = AvatarImageProcessor.get_emotion_images(emotion)

        if not selected_images:
            return

        if not AvatarAnimationService._is_window_open:
            cv2.namedWindow(AvatarAnimationService._window_name, cv2.WINDOW_NORMAL)
            AvatarAnimationService._is_window_open = True

        for img_path in selected_images:
            image = cv2.imread(os.path.join(image_folder, img_path))
            if image is not None:
                cv2.imshow(AvatarAnimationService._window_name, image)
                cv2.waitKey(100)  # Mostrar cada imagen por 100 ms

    @staticmethod
    def close_animation():
        """Cierra la ventana de animación cuando se detiene la detección."""
        if AvatarAnimationService._is_window_open:
            cv2.destroyWindow(AvatarAnimationService._window_name)
            AvatarAnimationService._is_window_open = False
