# contexts/avatar_management/infrastructure/renderers/viseme_renderer.py
import time
import pygame
from typing import Union, Mapping, Any, Tuple, List, Optional
from contexts.avatar_management.application.use_cases.generate_viseme_sequence_use_case import TimedViseme
from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService
from contexts.avatar_management.domain.services.viseme_mapping_service import VisemeMappingService

MIN_VISEME_MS = 40  # duración mínima de visema
AUDIO_LEAD_MS = 0  # compensación si el audio se adelanta (ajustar después de testear)


def _ratio_and_duration(v: Union[TimedViseme, Mapping[str, Any]]) -> Tuple[float, int]:
    """Extrae ratio y duración en ms desde TimedViseme o dict"""
    ratio = 0.5
    dur_ms = MIN_VISEME_MS

    if isinstance(v, TimedViseme):
        ratio = float(v.ratio or VisemeMappingService.viseme_ratio(v.viseme))
        dur_s = float(v.duration)
    elif isinstance(v, Mapping):
        name = str(v.get("viseme", "")).strip()
        ratio = float(v.get("ratio", VisemeMappingService.viseme_ratio(name)))
        dur_s = float(v.get("duration", 0.04))
    else:
        return ratio, dur_ms

    # Detectar si está en segundos o milisegundos
    if dur_s <= 5.0:
        dur_ms = int(max(MIN_VISEME_MS, dur_s * 1000))
    else:
        dur_ms = int(max(MIN_VISEME_MS, dur_s))

    ratio = max(0.0, min(1.0, ratio))
    return ratio, dur_ms


def _total_span_ms(visemes: List[Mapping[str, Any]]) -> int:
    """Calcula duración total del timeline de visemas"""
    if not visemes:
        return 0
    total = 0
    for item in visemes:
        start = int(item.get("start", 0))
        duration = int(item.get("duration", MIN_VISEME_MS))
        total = max(total, start + duration)
    return total


def _get_audio_duration_ms(audio_path: Optional[str]) -> Optional[int]:
    """Obtiene duración real del audio en milisegundos"""
    if not audio_path:
        return None

    try:
        import wave
        with wave.open(audio_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return int(1000 * frames / rate)
    except Exception as e:
        print(f"[WARN] No se pudo obtener duración del audio: {e}")
        return None


def _rescale_timeline(visemes: List[Mapping[str, Any]], target_ms: int) -> List[Mapping[str, Any]]:
    """Reescala el timeline para que coincida con la duración del audio"""
    src_ms = _total_span_ms(visemes)
    if src_ms <= 0 or target_ms <= 0:
        return visemes

    scale = target_ms / float(src_ms)
    print(f"[SYNC] Reescalando timeline: {src_ms}ms -> {target_ms}ms (factor={scale:.3f})")

    rescaled = []
    for item in visemes:
        start = int(item.get("start", 0) * scale)
        duration = int(max(MIN_VISEME_MS, item.get("duration", MIN_VISEME_MS) * scale))
        rescaled.append({**item, "start": start, "duration": duration})

    return rescaled


class VisemeRenderer:
    """
    Renderiza secuencia de visemas sincronizados con audio.
    Usa pygame.mixer.music como reloj maestro.
    """

    @staticmethod
    def render_sequence(
            visemes: List[Union[TimedViseme, Mapping[str, Any]]],
            emotion: str = "neutral",
            loop: bool = False,
            audio_path: Optional[str] = None,
    ) -> None:
        """
        Reproduce visemas sincronizados con audio.

        Args:
            visemes: Lista de visemas temporizados
            emotion: Emoción base del avatar (no usado en v3.0)
            loop: Si repetir la secuencia (no implementado)
            audio_path: Ruta al archivo WAV
        """
        try:
            # 1. NORMALIZAR ENTRADA: Convertir todo a dicts
            timeline: List[Mapping[str, Any]] = []
            for v in visemes or []:
                if isinstance(v, dict):
                    timeline.append(v)
                elif hasattr(v, "viseme"):  # TimedViseme
                    timeline.append({
                        "viseme": v.viseme,
                        "start": int(getattr(v, "start_time", 0) * 1000),
                        "duration": int(max(MIN_VISEME_MS, getattr(v, "duration", 0.08) * 1000)),
                        "ratio": float(getattr(v, "ratio", 0.6))
                    })

            if not timeline:
                print("[WARN] Timeline vacío, no hay visemas para renderizar")
                return

            # 2. OBTENER DURACIÓN REAL DEL AUDIO
            audio_duration_ms = _get_audio_duration_ms(audio_path)

            # 3. REESCALAR TIMELINE SI HAY AUDIO
            if audio_duration_ms:
                timeline = _rescale_timeline(timeline, audio_duration_ms)

            # 4. INICIALIZAR PYGAME MIXER
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("[INFO] Pygame mixer inicializado")

            # 5. CARGAR Y REPRODUCIR AUDIO **PRIMERO**
            audio_started = False
            start_time = None

            if audio_path:
                try:
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    start_time = time.perf_counter()
                    audio_started = True
                    print(f"[SYNC] Audio iniciado: {audio_path} ({audio_duration_ms}ms)")
                except Exception as e:
                    print(f"[ERROR] No se pudo reproducir audio: {e}")
                    audio_started = False

            # 6. ESPERAR A QUE EL AUDIO REALMENTE EMPIECE (crítico en Windows)
            if audio_started:
                time.sleep(0.05)  # 50ms de buffer para que pygame.mixer arranque

            # 7. RENDERIZAR VISEMAS SINCRONIZADOS
            if audio_started:
                print(f"[SYNC] Modo: Audio como reloj maestro")
                VisemeRenderer._render_with_audio_clock(timeline, start_time)
            else:
                print(f"[SYNC] Modo: Reloj interno (sin audio)")
                VisemeRenderer._render_with_internal_clock(timeline)

            print("[INFO] Vocalización completada")

        except Exception as e:
            print(f"[ERROR] render_sequence falló: {e}", flush=True)
            import traceback
            traceback.print_exc()
        finally:
            AvatarAnimationService.end_speaking()

    @staticmethod
    def _render_with_audio_clock(timeline: List[Mapping[str, Any]], audio_start_time: float):
        """Renderiza visemas usando pygame.mixer.music.get_pos() como reloj"""

        for item in timeline:
            viseme = str(item.get("viseme", "REST")).strip().upper()
            ratio, dur_ms = _ratio_and_duration(item)
            start_ms = int(item.get("start", 0))

            # ESPERA ACTIVA: Sincronizar con posición del audio
            target_time = audio_start_time + (start_ms / 1000.0) + (AUDIO_LEAD_MS / 1000.0)

            while True:
                current_time = time.perf_counter()

                # Verificar si el audio sigue reproduciéndose
                if not pygame.mixer.music.get_busy():
                    print("[WARN] Audio terminó antes de tiempo")
                    return

                # Si ya llegamos al tiempo objetivo, renderizar
                if current_time >= target_time:
                    break

                # Sleep corto para no consumir 100% CPU
                time.sleep(0.001)

            # Renderizar visema
            AvatarAnimationService.show_viseme(viseme, ratio=ratio, duration_ms=dur_ms)

    @staticmethod
    def _render_with_internal_clock(timeline: List[Mapping[str, Any]]):
        """Renderiza visemas usando time.perf_counter() (fallback sin audio)"""

        start_time = time.perf_counter()

        for item in timeline:
            viseme = str(item.get("viseme", "REST")).strip().upper()
            ratio, dur_ms = _ratio_and_duration(item)
            start_ms = int(item.get("start", 0))

            # Esperar hasta el tiempo de inicio del visema
            target_time = start_time + (start_ms / 1000.0)
            wait = target_time - time.perf_counter()

            if wait > 0:
                time.sleep(wait)

            # Renderizar visema
            AvatarAnimationService.show_viseme(viseme, ratio=ratio, duration_ms=dur_ms)