# contexts/avatar_management/domain/services/landmark_smoothing_service.py

import numpy as np

class LandmarkSmoothingService:
    """
    Aplica suavizado exponencial a una secuencia de puntos faciales (landmarks)
    para reducir el jitter y mejorar la estabilidad visual.
    """

    def __init__(self, alpha=0.6):
        """
        :param alpha: Factor de suavizado (0.0 - sin efecto, 1.0 - sin suavizado)
        """
        self.alpha = alpha
        self.previous_landmarks = None

    def smooth(self, current_landmarks):
        """
        Aplica suavizado a los landmarks actuales con respecto al estado anterior.

        :param current_landmarks: np.ndarray con shape (N, 2) o (N, 3)
        :return: np.ndarray suavizado
        """
        if not isinstance(current_landmarks, np.ndarray):
            raise ValueError("Los landmarks deben ser un np.ndarray.")

        if self.previous_landmarks is None:
            self.previous_landmarks = current_landmarks.copy()
            return current_landmarks

        # Aplicamos suavizado exponencial
        smoothed = self.alpha * current_landmarks + (1 - self.alpha) * self.previous_landmarks
        self.previous_landmarks = smoothed
        return smoothed
