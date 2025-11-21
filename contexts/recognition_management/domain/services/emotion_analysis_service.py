# contexts/recognition_management/domain/services/emotion_analysis_service.py

from contexts.recognition_management.domain.entities.emotion import Emotion
from contexts.recognition_management.infrastructure.processors.image_processing import ImageProcessor
from fer import FER

class EmotionAnalysisService:
    def __init__(self):
        self.detector = FER(mtcnn=True)

    def analyze_emotion(self, image_data) -> Emotion:
        preprocessed_image = ImageProcessor.preprocess(image_data)
        results = self.detector.top_emotion(preprocessed_image)

        if results:
            emotion, score = results
            return Emotion(detected_emotion=emotion, confidence=score)

        return Emotion(detected_emotion=None, confidence=None)
