from contexts.recognition_management.infrastructure.processors.image_processing import ImageProcessor
from contexts.recognition_management.infrastructure.adapters.mediapipe_adapter import MediaPipeAdapter

class FacialRecognitionUseCase:
    @staticmethod
    def process_face_data(image_data):
        """
        Recibe una imagen en formato binario y la envía a MediaPipe para reconocimiento facial.
        """
        processed_image = ImageProcessor.preprocess(image_data)
        emotion_result = MediaPipeAdapter.detect_emotion(processed_image)
        return emotion_result

    @staticmethod
    def analyze_images_for_avatar():
        """
        Procesa imágenes en lote para generar landmarks faciales.
        """
        return ImageProcessor.batch_process_images()
