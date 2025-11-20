# contexts/recognition_management/infrastructure/processors/realtime_emotion_detector.py
import cv2
import numpy as np
from typing import Any, Callable, Optional, Tuple
from fer import FER
import mediapipe as mp

# ===================== Config por defecto =====================
DEFAULT_CAMERA_SIZE: Tuple[int, int] = (424, 240)   # ancho, alto (más chico = menos latencia)
DEFAULT_FER_EVERY_N_FRAMES = 1                      # 1 = cada frame
DEFAULT_SHOW_CAMERA = False
DEFAULT_VERBOSE = True

# ===================== Estado simple =====================
_current_emotion = "neutral"
_stop_flag = False

# ===================== Pipelines de reconocimiento =====================
_emotion_detector = FER(mtcnn=False)

_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# ===================== Mapeo empático (ajústalo a tu UX) =====================
_EMPATHY_MAP = {
    "happy": "happy",
    "sad": "sad",
    "angry": "angry",
    "disgust": "neutral",
    "fear": "fear",
    "surprise": "surprise",
    None: "neutral",
}
_DEFAULT_AVATAR_EMO = "neutral"


def _map_emotion_for_avatar(user_emotion: Optional[str]) -> str:
    ue = (user_emotion or "").lower()
    return _EMPATHY_MAP.get(ue, _DEFAULT_AVATAR_EMO)


# --- helper seguro para imprimir porcentajes ---
def _fmt_pct(x) -> str:
    try:
        v = float(x)
        if np.isnan(v):
            v = 0.0
    except Exception:
        v = 0.0
    return f"{v*100:.0f}%"


# ==========================================================
# ===============   LOOP PRINCIPAL (GENÉRICO)  =============
# ==========================================================
def detect_real_time_emotions_and_landmarks(
    *,
    on_emotion: Optional[Callable[[str, float], None]] = None,
    on_landmarks: Optional[Callable[[np.ndarray], None]] = None,
    camera_size: Tuple[int, int] = DEFAULT_CAMERA_SIZE,
    fer_every_n_frames: int = DEFAULT_FER_EVERY_N_FRAMES,
    show_camera_window: bool = DEFAULT_SHOW_CAMERA,
    verbose: bool = DEFAULT_VERBOSE,
) -> None:
    """
    Captura webcam -> FER -> landmarks -> callbacks.

    - Si no pasas callbacks, solo loguea en consola.
    - NO muestra la cámara a menos que show_camera_window=True.
    """

    global _current_emotion, _stop_flag

    def _default_on_emotion(emotion: str, score: float) -> None:
        if verbose:
            print(f"[AVATAR-EMO] emotion={emotion} score={score:.3f}", flush=True)

    def _default_on_landmarks(lms: np.ndarray) -> None:
        if verbose:
            print(f"[AVATAR-LM] landmarks shape={lms.shape}", flush=True)

    on_emotion = on_emotion or _default_on_emotion
    on_landmarks = on_landmarks or _default_on_landmarks

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara.", flush=True)
        return

    # Resolución baja para menor consumo
    w, h = camera_size
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    if verbose:
        print(
            f"[FER] Captura iniciada: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
            f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} (ventana cámara={'ON' if show_camera_window else 'OFF'})",
            flush=True,
        )

    frame_id = 0
    _current_emotion = "neutral"
    _stop_flag = False

    try:
        while not _stop_flag:
            ok, frame = cap.read()
            if not ok:
                continue
            frame_id += 1

            # espejo
            frame = cv2.flip(frame, 1)

            # ------------ FER ------------
            if frame_id % max(1, fer_every_n_frames) == 0:
                try:
                    emo, score = _emotion_detector.top_emotion(frame)  # (emo, prob) o (None, None)
                except Exception:
                    emo, score = None, 0.0

                mapped = _map_emotion_for_avatar(emo)

                if verbose:
                    print(f"[FER] raw={emo} ({_fmt_pct(score)}) -> avatar={mapped}", flush=True)

                if mapped and mapped != _current_emotion:
                    _current_emotion = mapped
                    on_emotion(mapped, float(score or 0.0))

            # --------- Landmarks ----------
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results_any: Any = _face_mesh.process(rgb)  # type: ignore
            except Exception:
                results_any = None

            if results_any and getattr(results_any, "multi_face_landmarks", None):
                face_lm = results_any.multi_face_landmarks[0]
                lms = np.array([(lm.x, lm.y, lm.z) for lm in face_lm.landmark], dtype=np.float32)

                # Asegurar (N,3); si viene (T,N,3) nos quedamos con el último frame
                lms = np.asarray(lms)
                if lms.ndim == 3:
                    lms = lms[-1]
                if lms.ndim == 2 and lms.shape[0] >= 3:
                    on_landmarks(lms)

            # --------- Cámara opcional ----------
            if show_camera_window:
                cv2.imshow("FER (debug)", frame)
                if (cv2.waitKey(1) & 0xFF) == ord('q'):
                    _stop_flag = True
                    break

    finally:
        try:
            cap.release()
        except Exception:
            pass
        if show_camera_window:
            try:
                cv2.destroyWindow("FER (debug)")
            except Exception:
                pass


# ==========================================================
# ==============  WRAPPER COMPATIBLE CON app.py  ===========
# ==========================================================
def run_realtime_detector(
    *,
    on_emotion: Optional[Callable[[str, float], None]] = None,
    on_landmarks: Optional[Callable[[np.ndarray], None]] = None,
    camera_size: Tuple[int, int] = DEFAULT_CAMERA_SIZE,
    fer_every_n_frames: int = DEFAULT_FER_EVERY_N_FRAMES,
    show_camera_window: bool = DEFAULT_SHOW_CAMERA,
    verbose: bool = DEFAULT_VERBOSE,
) -> None:
    """Alias con misma firma que importan tus use cases."""
    detect_real_time_emotions_and_landmarks(
        on_emotion=on_emotion,
        on_landmarks=on_landmarks,
        camera_size=camera_size,
        fer_every_n_frames=fer_every_n_frames,
        show_camera_window=show_camera_window,
        verbose=verbose,
    )
