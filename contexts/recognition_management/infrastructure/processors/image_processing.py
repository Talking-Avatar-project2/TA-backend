import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def preprocess(image_data):
        """
        Preprocesa una imagen convirtiéndola a escala de grises y ajustando el brillo y contraste.
        :param image_data: Imagen en formato binario.
        :return: Imagen preprocesada en formato BGR.
        """
        try:
            # Convertir datos binarios a una imagen
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Convertir a escala de grises
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Ajustar brillo y contraste
            adjusted_image = cv2.convertScaleAbs(gray_image, alpha=1.5, beta=20)  # Parámetros ajustables

            # Volver a convertir a BGR para compatibilidad con modelos de reconocimiento facial
            return cv2.cvtColor(adjusted_image, cv2.COLOR_GRAY2BGR)
        except Exception as e:
            print(f"Error en ImageProcessor: {e}")
            return None
