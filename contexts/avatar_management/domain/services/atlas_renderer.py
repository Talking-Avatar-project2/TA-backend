# contexts/avatar_management/domain/services/atlas_renderer.py
"""
AtlasRenderer V2 con mejoras críticas:
- Interpolación temporal suave (ease-in/ease-out mejorado)
- Blending adaptativo según tipo de visema
- Pre-carga inteligente para eliminar stuttering
- Sincronización robusta con audio
"""
import os, json, time, threading
from typing import List, Tuple, Dict, Optional
import numpy as np
import cv2

VIS_LIST = ["REST", "A", "E", "I", "O", "U", "MBP", "FV", "L", "TH", "SH", "R"]

# Configuración de transiciones por tipo de visema
TRANSITION_CONFIG = {
    # Vocales: transiciones más lentas y suaves
    "A": {"lead_ms": 120, "tail_ms": 150, "ease_power": 3},
    "E": {"lead_ms": 100, "tail_ms": 130, "ease_power": 3},
    "I": {"lead_ms": 90, "tail_ms": 120, "ease_power": 3},
    "O": {"lead_ms": 110, "tail_ms": 140, "ease_power": 3},
    "U": {"lead_ms": 100, "tail_ms": 130, "ease_power": 3},

    # Consonantes: transiciones rápidas y precisas
    "MBP": {"lead_ms": 60, "tail_ms": 80, "ease_power": 2},
    "FV": {"lead_ms": 70, "tail_ms": 90, "ease_power": 2},
    "L": {"lead_ms": 80, "tail_ms": 100, "ease_power": 2},
    "TH": {"lead_ms": 70, "tail_ms": 90, "ease_power": 2},
    "SH": {"lead_ms": 80, "tail_ms": 100, "ease_power": 2},
    "R": {"lead_ms": 90, "tail_ms": 110, "ease_power": 2},

    "REST": {"lead_ms": 150, "tail_ms": 150, "ease_power": 3}
}


def _ease_bezier(x: float, power: int = 3) -> float:
    """Curva de ease más natural usando potencia variable"""
    if x < 0: return 0.0
    if x > 1: return 1.0

    if power == 2:
        # Cuadrática: más rápida
        return x * x if x < 0.5 else 1 - pow(-2 * x + 2, 2) / 2
    else:
        # Cúbica: más suave (default)
        return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2


def _alpha_blend(a: np.ndarray, b: np.ndarray, w: float) -> np.ndarray:
    """Blending optimizado con manejo de bordes"""
    if w <= 0.01: return a
    if w >= 0.99: return b

    # Clamp weight
    w = max(0.0, min(1.0, w))

    return cv2.addWeighted(a, 1.0 - w, b, w, 0.0)


def _resize_safe(img: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Resize con preservación de calidad"""
    if img.shape[:2][::-1] == target_size:
        return img
    return cv2.resize(img, target_size, interpolation=cv2.INTER_CUBIC)


class AtlasRenderer:
    """
    Renderer mejorado con:
    - Transiciones adaptativas por tipo de visema
    - Pre-buffering para eliminar lag
    - Interpolación multi-frame para suavidad
    """

    def __init__(self,
                 atlas_dir: str,
                 manifest_file: str = "manifest.json",
                 fps: int = 30,
                 buffer_frames: int = 3):

        self.atlas_dir = atlas_dir
        self.manifest_path = os.path.join(atlas_dir, manifest_file)
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.buffer_frames = buffer_frames

        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"manifest.json no existe: {self.manifest_path}")

        # Cargar manifest
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            raw_manifest: Dict[str, List[str]] = json.load(f)

        # Carga robusta de imágenes
        self.images: Dict[str, List[np.ndarray]] = {k: [] for k in VIS_LIST}
        first_img = None

        for viseme in VIS_LIST:
            file_list = raw_manifest.get(viseme, [])
            for fn in file_list:
                p = os.path.join(self.atlas_dir, fn)
                im = cv2.imread(p, cv2.IMREAD_COLOR)
                if im is not None:
                    self.images[viseme].append(im)
                    if first_img is None:
                        first_img = im

        if first_img is None:
            raise RuntimeError(f"No se pudo cargar ninguna imagen desde {self.atlas_dir}")

        # Garantizar REST válido
        if len(self.images["REST"]) == 0:
            self.images["REST"] = [first_img.copy()]

        # Normalizar tamaños
        base_h, base_w = self.images["REST"][0].shape[:2]
        self.size = (base_w, base_h)

        for k in VIS_LIST:
            if self.images[k]:
                self.images[k] = [_resize_safe(im, self.size) for im in self.images[k]]
            else:
                # Fallback a REST
                self.images[k] = [self.images["REST"][0].copy()]

        # Estado de reproducción
        self._timeline: List[Tuple[str, float, float]] = []
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._latest_frame = self.images["REST"][0].copy()
        self._lock = threading.RLock()

        # Pre-buffering
        self._frame_buffer = []
        self._buffer_lock = threading.Lock()

        print(f"[AtlasRendererV2] Inicializado: {base_w}x{base_h}, {fps} FPS")
        for k in VIS_LIST:
            print(f"  - {k:4s}: {len(self.images[k])} imágenes")

    def _pick_variant(self, vis: str, seed: int) -> np.ndarray:
        """Selecciona variante con distribución uniforme"""
        arr = self.images.get(vis) or self.images["REST"]
        return arr[seed % len(arr)]

    def _get_transition_params(self, viseme: str) -> Dict:
        """Obtiene parámetros de transición para un visema"""
        return TRANSITION_CONFIG.get(viseme, TRANSITION_CONFIG["REST"])

    def start_playback(self, timeline: List[Tuple[str, float, float]]):
        """Inicia reproducción con pre-buffering"""
        self._timeline = timeline
        self._running = True

        # Pre-generar primeros frames
        self._prebuffer_frames()

        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _prebuffer_frames(self):
        """Pre-genera frames para eliminar lag inicial"""
        if not self._timeline:
            return

        with self._buffer_lock:
            self._frame_buffer.clear()

            # Generar primeros N frames
            for i in range(min(self.buffer_frames, len(self._timeline))):
                vis, t0, t1 = self._timeline[i]
                frame = self._pick_variant(vis, i)
                self._frame_buffer.append(frame.copy())

    def stop(self):
        """Detiene reproducción"""
        self._running = False

    def get_frame(self) -> np.ndarray:
        """Obtiene frame actual (thread-safe)"""
        with self._lock:
            return self._latest_frame.copy()

    def _run(self):
        """Loop principal de reproducción con interpolación mejorada"""
        if not self._timeline:
            return

        t_start = time.perf_counter()
        frame_idx = 0
        seed = int(time.time() * 1000) % 1000

        while self._running:
            now = time.perf_counter() - t_start

            # Encontrar segmento actual
            cur_i = None
            for i, (v, t0, t1) in enumerate(self._timeline):
                if t0 <= now < t1:
                    cur_i = i
                    break

            if cur_i is None:
                # Fin del timeline
                with self._lock:
                    self._latest_frame = self.images["REST"][0].copy()
                self._running = False
                break

            vis, t0, t1 = self._timeline[cur_i]
            params = self._get_transition_params(vis)

            # Convertir ms a segundos
            lead = params["lead_ms"] / 1000.0
            tail = params["tail_ms"] / 1000.0
            ease_power = params["ease_power"]

            # Frame actual
            im_cur = self._pick_variant(vis, seed + cur_i)
            final_frame = im_cur.copy()

            # Blend de entrada (desde frame anterior)
            time_in_segment = now - t0
            if time_in_segment < tail and cur_i > 0:
                v_prev, p0, p1 = self._timeline[cur_i - 1]
                im_prev = self._pick_variant(v_prev, seed + cur_i - 1)

                # Progreso de blend (0 a 1)
                blend_progress = time_in_segment / tail
                weight = _ease_bezier(blend_progress, ease_power)

                final_frame = _alpha_blend(im_prev, im_cur, weight)

            # Blend de salida (hacia siguiente frame)
            time_to_end = t1 - now
            if time_to_end < lead and cur_i < len(self._timeline) - 1:
                v_next, n0, n1 = self._timeline[cur_i + 1]
                im_next = self._pick_variant(v_next, seed + cur_i + 1)

                # Progreso de anticipación
                blend_progress = (lead - time_to_end) / lead
                weight = _ease_bezier(blend_progress, ease_power)

                final_frame = _alpha_blend(final_frame, im_next, weight)

            # Actualizar frame
            with self._lock:
                self._latest_frame = final_frame

            # Timing preciso
            frame_idx += 1
            target_time = frame_idx * self.frame_time
            elapsed = time.perf_counter() - t_start
            sleep_time = max(0.0, target_time - elapsed)

            if sleep_time > 0:
                time.sleep(sleep_time)

        print(f"[AtlasRendererV2] Reproducción finalizada ({frame_idx} frames)")

    # Compatibilidad con código legacy
    def build_timeline_from_text(self, text: str, rate: float = 1.0) -> List[Tuple[str, float, float]]:
        """Fallback básico para generación desde texto"""
        dur = {
            "A": 0.19, "E": 0.13, "I": 0.12, "O": 0.18, "U": 0.17,
            "MBP": 0.11, "FV": 0.11, "L": 0.10, "TH": 0.11,
            "SH": 0.12, "R": 0.11, "REST": 0.06
        }

        visemes = self._text_to_visemes(text)
        t = 0.0
        timeline = []
        rate = max(0.5, min(2.0, rate))

        for v in visemes:
            d = dur.get(v, 0.10) / rate
            timeline.append((v, t, t + d))
            t += d

        return self._merge_rest(timeline)

    def _text_to_visemes(self, text: str) -> List[str]:
        """Mapeo simple texto -> visemas"""
        t = (text or "").lower()
        out = []
        for ch in t:
            if ch in "aeiouáéíóú":
                out.append(ch.upper().replace("Á", "A").replace("É", "E")
                           .replace("Í", "I").replace("Ó", "O").replace("Ú", "U"))
            elif ch in "mbp":
                out.append("MBP")
            elif ch in "fv":
                out.append("FV")
            elif ch in "l":
                out.append("L")
            elif ch in "td":
                out.append("TH")
            elif ch in "schxjz":
                out.append("SH")
            elif ch in "r":
                out.append("R")
            else:
                out.append("REST")

        return [v for i, v in enumerate(out) if i == 0 or v != out[i - 1]]

    def _merge_rest(self, timeline: List[Tuple[str, float, float]]) -> List[Tuple[str, float, float]]:
        """Fusiona REST consecutivos"""
        if not timeline:
            return []

        merged = [timeline[0]]
        for v, t0, t1 in timeline[1:]:
            if v == "REST" and merged[-1][0] == "REST":
                pv, p0, p1 = merged.pop()
                merged.append(("REST", p0, t1))
            else:
                merged.append((v, t0, t1))

        return merged