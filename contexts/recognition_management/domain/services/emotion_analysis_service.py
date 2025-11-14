from contexts.recognition_management.domain.entities.emotion import Emotion
from contexts.recognition_management.infrastructure.processors.image_processing import ImageProcessor
from fer import FER

class EmotionAnalysisService:
    def __init__(self):
        """Carga del modelo de reconocimiento de emociones."""
        self.detector = FER(mtcnn=True)

    def analyze_emotion(self, image_data) -> Emotion:
        """
        Analiza la emoción en una imagen preprocesada.
        :param image_data: Datos binarios de la imagen.
        :return: Objeto Emotion con la emoción detectada y su confianza.
        """
        preprocessed_image = ImageProcessor.preprocess(image_data)
        results = self.detector.top_emotion(preprocessed_image)

        if results:
            emotion, score = results
            return Emotion(detected_emotion=emotion, confidence=score)
        return Emotion(detected_emotion=None, confidence=None)
