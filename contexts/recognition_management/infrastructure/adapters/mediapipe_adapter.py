import os
import sys
import cv2
import argparse
import numpy as np

try:
    import mediapipe as mp
except ImportError as e:
    raise ImportError("Falta MediaPipe. Instala con: pip install mediapipe") from e


class MediaPipeAdapter:
    """
    Adaptador MediaPipe para reconocimiento facial y generación del avatar neutral.
    """

    @staticmethod
    def generate_avatar_landmarks(image_path: str, out_dir: str = "images/avatar_final") -> str:
        """
        Genera los landmarks base del avatar (468x3) en píxeles, sin overlay visible.
        Guarda:
          - neutral_processed.png
          - neutral_landmarks.npy
        """
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"No existe la imagen: {image_path}")

        os.makedirs(out_dir, exist_ok=True)

        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise ValueError(f"No se pudo leer la imagen: {image_path}")

        h, w = img_bgr.shape[:2]
        mp_face_mesh = mp.solutions.face_mesh

        # Forzamos refine_landmarks=False → 468 puntos exactos
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            res = face_mesh.process(img_rgb)

        if not res.multi_face_landmarks:
            raise RuntimeError("No se detectó rostro en la imagen neutral.")

        lms = res.multi_face_landmarks[0].landmark
        n = len(lms)
        if n != 468:
            raise RuntimeError(f"Se esperaban 468 puntos, pero se obtuvieron {n}.")

        # Convertimos a coordenadas en píxeles
        lm_px = np.zeros((n, 3), dtype=np.float32)
        for i, lm in enumerate(lms):
            lm_px[i] = [lm.x * w, lm.y * h, lm.z]

        # Guardamos la imagen neutral sin overlay ni wireframe
        neutral_path = os.path.join(out_dir, "neutral_processed.png")
        npy_path = os.path.join(out_dir, "neutral_landmarks.npy")

        cv2.imwrite(neutral_path, img_bgr)
        np.save(npy_path, lm_px.astype(np.float32))

        print(f"[OK] Imagen neutral guardada en: {neutral_path}")
        print(f"[OK] Landmarks guardados en: {npy_path} (shape={lm_px.shape})")
        return npy_path


# CLI opcional
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera neutral_landmarks.npy (468x3) para el avatar base.")
    parser.add_argument("--make-avatar", type=str, metavar="IMG",
                        help="Ruta a la imagen neutral (ej: images/avatar_base/neutral.png)")
    parser.add_argument("--out", type=str, default="images/avatar_final",
                        help="Carpeta de salida (default: images/avatar_final)")
    args = parser.parse_args()

    if args.make_avatar:
        MediaPipeAdapter.generate_avatar_landmarks(args.make_avatar, out_dir=args.out)
        sys.exit(0)

    print("Uso:\n  python contexts/recognition_management/infrastructure/adapters/mediapipe_adapter.py "
          "--make-avatar images/avatar_base/neutral.png --out images/avatar_final")
