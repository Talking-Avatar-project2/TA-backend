import cv2
import mediapipe as mp
import numpy as np


class MediaPipeAdapter:
    face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True)

    @staticmethod
    def process_image(image_data):
        """
        Procesa una imagen con MediaPipe para extraer landmarks faciales.
        :param image_data: Imagen en formato binario.
        :return: Diccionario con landmarks detectados o mensaje de error.
        """
        try:
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            results = MediaPipeAdapter.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if results.multi_face_landmarks:
                landmarks_list = []
                for face_landmarks in results.multi_face_landmarks:
                    for landmark in face_landmarks.landmark:
                        landmarks_list.append((landmark.x, landmark.y, landmark.z))
                return {"landmarks": landmarks_list}

            return {"error": "No face landmarks detected"}
        except Exception as e:
            return {"error": f"Error en MediaPipeAdapter: {str(e)}"}

    @staticmethod
    def batch_process_images(image_list):
        """
        Procesa una lista de imágenes con MediaPipe.
        :param image_list: Lista de imágenes en formato binario.
        :return: Lista de diccionarios con landmarks detectados.
        """
        processed_results = []
        for image_data in image_list:
            result = MediaPipeAdapter.process_image(image_data)
            processed_results.append(result)
        return processed_results
