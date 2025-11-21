# contexts/recognition_management/infrastructure/processors/realtime_emotion_detector.py

import cv2
import numpy as np
from typing import Any, Callable, Optional, Tuple
from fer import FER
import mediapipe as mp

DEFAULT_CAMERA_SIZE: Tuple[int, int] = (424, 240)
DEFAULT_FER_EVERY_N_FRAMES = 1
DEFAULT_SHOW_CAMERA = False
DEFAULT_VERBOSE = True

_current_emotion = "neutral"
_stop_flag = False

def stop_global_detector():
    global _stop_flag
    _stop_flag = True

_emotion_detector = FER(mtcnn=False)

_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

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


def _fmt_pct(x) -> str:
    try:
        v = float(x)
        if np.isnan(v):
            v = 0.0
    except Exception:
        v = 0.0
    return f"{v*100:.0f}%"


def detect_real_time_emotions_and_landmarks(
    *,
    on_emotion: Optional[Callable[[str, float], None]] = None,
    on_landmarks: Optional[Callable[[np.ndarray], None]] = None,
    stop_condition: Optional[Callable[[], bool]] = None,  # NUEVO
    camera_size: Tuple[int, int] = DEFAULT_CAMERA_SIZE,
    fer_every_n_frames: int = DEFAULT_FER_EVERY_N_FRAMES,
    show_camera_window: bool = DEFAULT_SHOW_CAMERA,
    verbose: bool = DEFAULT_VERBOSE,
) -> None:

    global _current_emotion, _stop_flag

    def _default_on_emotion(emotion: str, score: float) -> None:
        if verbose:
            print(f"[AVATAR-EMO] {emotion} ({score:.3f})", flush=True)

    def _default_on_landmarks(lms: np.ndarray) -> None:
        if verbose:
            print(f"[AVATAR-LM] landmarks shape={lms.shape}", flush=True)

    on_emotion = on_emotion or _default_on_emotion
    on_landmarks = on_landmarks or _default_on_landmarks
    stop_condition = stop_condition or (lambda: False)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara.", flush=True)
        return

    w, h = camera_size
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    if verbose:
        print(f"[FER] Captura iniciada {w}x{h}", flush=True)

    frame_id = 0
    _current_emotion = "neutral"
    _stop_flag = False

    try:
        while not stop_condition() and not _stop_flag:
            ok, frame = cap.read()
            if not ok:
                continue

            frame_id += 1
            frame = cv2.flip(frame, 1)

            if frame_id % max(1, fer_every_n_frames) == 0:
                try:
                    emo, score = _emotion_detector.top_emotion(frame)
                except Exception:
                    emo, score = None, 0.0

                mapped = _map_emotion_for_avatar(emo)

                if verbose:
                    print(f"[FER] raw={emo} conf={_fmt_pct(score)} -> {mapped}", flush=True)

                if mapped != _current_emotion:
                    _current_emotion = mapped
                    on_emotion(mapped, float(score or 0.0))

            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results_any: Any = _face_mesh.process(rgb)
            except Exception:
                results_any = None

            if results_any and getattr(results_any, "multi_face_landmarks", None):
                face_lm = results_any.multi_face_landmarks[0]
                lms = np.array([(lm.x, lm.y, lm.z) for lm in face_lm.landmark], dtype=np.float32)

                if lms.ndim == 2 and lms.shape[0] >= 3:
                    on_landmarks(lms)

            if show_camera_window:
                cv2.imshow("FER (debug)", frame)
                if (cv2.waitKey(1) & 0xFF) == ord("q"):
                    break

    finally:
        try:
            cap.release()
        except:
            pass

        if show_camera_window:
            try:
                cv2.destroyWindow("FER (debug)")
            except:
                pass


def run_realtime_detector(
    *,
    on_emotion: Optional[Callable[[str, float], None]] = None,
    on_landmarks: Optional[Callable[[np.ndarray], None]] = None,
    stop_condition: Optional[Callable[[], bool]] = None,  # NUEVO
    camera_size: Tuple[int, int] = DEFAULT_CAMERA_SIZE,
    fer_every_n_frames: int = DEFAULT_FER_EVERY_N_FRAMES,
    show_camera_window: bool = DEFAULT_SHOW_CAMERA,
    verbose: bool = DEFAULT_VERBOSE,
) -> None:
    detect_real_time_emotions_and_landmarks(
        on_emotion=on_emotion,
        on_landmarks=on_landmarks,
        stop_condition=stop_condition,  # NUEVO
        camera_size=camera_size,
        fer_every_n_frames=fer_every_n_frames,
        show_camera_window=show_camera_window,
        verbose=verbose,
    )
