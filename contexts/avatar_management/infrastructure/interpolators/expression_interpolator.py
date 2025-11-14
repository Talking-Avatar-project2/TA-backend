#contexts/avatar_management/infrastructure/interpolators/expression_interpolator.py

import cv2
import numpy as np
from typing import List
import os


class ExpressionInterpolator:
    """
    Clase para interpolar entre imágenes de una expresión facial
    y generar una transición visual más fluida entre ellas.
    """

    def __init__(self, interpolation_steps: int = 2):
        """
        :param interpolation_steps: número de imágenes interpoladas entre cada par consecutivo
        """
        self.interpolation_steps = interpolation_steps

    def interpolate_sequence(self, image_paths: List[str]) -> List[np.ndarray]:
        """
        Dado una lista de rutas de imágenes, devuelve una secuencia interpolada de imágenes.

        :param image_paths: rutas de imágenes base
        :return: lista de imágenes interpoladas como matrices numpy
        """
        if not image_paths:
            raise ValueError("La lista de imágenes no puede estar vacía.")

        interpolated_sequence = []

        for i in range(len(image_paths) - 1):
            img1 = self._load_image(image_paths[i])
            img2 = self._load_image(image_paths[i + 1])

            # Insertar imagen original
            interpolated_sequence.append(img1)

            # Crear pasos intermedios
            for step in range(1, self.interpolation_steps + 1):
                alpha = step / (self.interpolation_steps + 1)
                interpolated = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
                interpolated_sequence.append(interpolated)

        # Agregar última imagen
        interpolated_sequence.append(self._load_image(image_paths[-1]))

        return interpolated_sequence

    def _load_image(self, path: str) -> np.ndarray:
        """
        Carga una imagen y la convierte a RGB.
        :param path: ruta relativa
        :return: imagen como array numpy
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró la imagen: {path}")
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
