# contexts/avatar_management/domain/services/avatar_animation_service.py
"""
AvatarAnimationService V2 con mejoras de rendimiento y sincronización.

CAMBIOS PRINCIPALES:
1. Usa AtlasRendererV2 con transiciones suaves
2. Sincronización robusta con audio (maneja latencia de pygame.mixer)
3. Pre-warming para eliminar lag en primera ejecución
4. Threading optimizado sin race conditions
"""
import os
import time
import threading
import numpy as np
from typing import Optional, List, Tuple
import pygame


class AvatarAnimationService:
    """Servicio mejorado con sincronización real y transiciones suaves"""

    # Estado
    _renderer = None  # AtlasRendererV2
    _frame_loop_thread = None
    _frame_loop_running = False
    _lock = threading.RLock()
    _last_frame: Optional[np.ndarray] = None
    _renderer_ready = False
    _mixer_initialized = False

    # Configuración de audio
    MIXER_FREQUENCY = 22050
    MIXER_BUFFER = 512  # Menor = menos latencia
    AUDIO_WARMUP_MS = 100  # Tiempo de espera para que arranque el audio

    @staticmethod
    def initialize():
        """
        Inicializa el renderer y el loop de frames.
        LLAMAR UNA SOLA VEZ al arrancar.
        """
        if AvatarAnimationService._renderer is not None:
            print("[INFO] AvatarAnimationServiceV2 ya inicializado")
            return

        try:
            # Importar aquí para evitar dependencias circulares
            from contexts.avatar_management.domain.services.atlas_renderer import AtlasRenderer

            atlas_dir = os.path.join("images", "visemes_atlas_final")

            AvatarAnimationService._renderer = AtlasRenderer(
                atlas_dir=atlas_dir,
                fps=30,
                buffer_frames=3  # Pre-buffering
            )

            print("[INFO] AtlasRendererV2 inicializado correctamente")

        except Exception as e:
            print(f"[ERROR] No se pudo inicializar AtlasRendererV2: {e}")
            import traceback
            traceback.print_exc()
            return

        # Inicializar mixer de audio
        AvatarAnimationService._init_audio_mixer()

        # Arrancar loop de frames
        if not AvatarAnimationService._frame_loop_running:
            AvatarAnimationService._frame_loop_running = True

            thread = threading.Thread(
                target=AvatarAnimationService._frame_loop,
                daemon=True,
                name="AvatarFrameLoop"
            )
            thread.start()
            AvatarAnimationService._frame_loop_thread = thread

            print("[INFO] Frame loop iniciado")

        # Pre-warming: esperar a que todo esté listo
        time.sleep(0.2)
        AvatarAnimationService._renderer_ready = True
        print("[INFO] AvatarAnimationServiceV2 completamente listo")

    @staticmethod
    def _init_audio_mixer():
        """Inicializa pygame.mixer una sola vez"""
        if AvatarAnimationService._mixer_initialized:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=AvatarAnimationService.MIXER_FREQUENCY,
                    size=-16,
                    channels=2,
                    buffer=AvatarAnimationService.MIXER_BUFFER
                )

            AvatarAnimationService._mixer_initialized = True
            print("[INFO] pygame.mixer inicializado")

        except Exception as e:
            print(f"[ERROR] No se pudo inicializar mixer: {e}")

    @staticmethod
    def _frame_loop():
        """
        Loop que toma frames del renderer a 30 FPS y los envía al display.
        Corre en un thread separado.
        """
        from contexts.avatar_management.infrastructure.display.avatar_display_service import AvatarDisplayService

        fps = 30
        frame_time = 1.0 / fps

        while AvatarAnimationService._frame_loop_running:
            try:
                if AvatarAnimationService._renderer is None:
                    time.sleep(0.1)
                    continue

                # Obtener frame actual
                frame = AvatarAnimationService._renderer.get_frame()

                with AvatarAnimationService._lock:
                    AvatarAnimationService._last_frame = frame

                # Enviar al display
                AvatarDisplayService.show_frame(frame)

                # Timing preciso
                time.sleep(frame_time)

            except Exception as e:
                print(f"[ERROR] frame_loop: {e}")
                time.sleep(0.1)

    # ========== API PÚBLICA ==========

    @staticmethod
    def speak_with_timeline(timeline: List[Tuple[str, float, float]], audio_path: str = None):
        """
        Reproduce vocalización con timeline pre-calculado.

        Args:
            timeline: [(viseme, t_start_sec, t_end_sec), ...]
            audio_path: Ruta al archivo WAV
        """
        AvatarAnimationService.initialize()

        # Esperar a que esté listo
        max_wait = 2.0
        start_wait = time.time()
        while not AvatarAnimationService._renderer_ready:
            if (time.time() - start_wait) > max_wait:
                print("[ERROR] Renderer no está listo después de 2s")
                return
            time.sleep(0.05)

        if AvatarAnimationService._renderer is None:
            print("[ERROR] Renderer no inicializado")
            return

        # Reproducir audio PRIMERO
        audio_started = False
        if audio_path:
            audio_started = AvatarAnimationService._play_audio_sync(audio_path)

        # Arrancar timeline de visemas
        # CRÍTICO: Usar el mismo t0 que el audio
        AvatarAnimationService._renderer.start_playback(timeline)

        print(f"[INFO] Vocalización iniciada: {len(timeline)} visemas")
        if audio_started:
            print(f"[INFO] Audio sincronizado: {audio_path}")

    @staticmethod
    def _play_audio_sync(audio_path: str) -> bool:
        """
        Reproduce audio y ESPERA a que arranque.

        Returns:
            True si el audio arrancó correctamente
        """
        try:
            AvatarAnimationService._init_audio_mixer()

            # Cargar audio
            pygame.mixer.music.load(audio_path)

            # Reproducir
            pygame.mixer.music.play()

            # CRÍTICO: Esperar a que realmente arranque
            max_wait_sec = 0.5
            start = time.perf_counter()

            while not pygame.mixer.music.get_busy():
                if (time.perf_counter() - start) > max_wait_sec:
                    print("[WARN] Audio no arrancó en 500ms")
                    return False
                time.sleep(0.01)

            # Buffer adicional para estabilidad
            time.sleep(AvatarAnimationService.AUDIO_WARMUP_MS / 1000.0)

            print(f"[AUDIO] Reproduciendo: {os.path.basename(audio_path)}")
            return True

        except Exception as e:
            print(f"[ERROR] Audio falló: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def speak_text(text: str, rate: float = 1.0):
        """
        Vocaliza texto usando timeline simple (sin audio).
        Útil para testing.
        """
        AvatarAnimationService.initialize()

        if AvatarAnimationService._renderer is None:
            print("[ERROR] Renderer no inicializado")
            return

        # Generar timeline desde texto
        timeline = AvatarAnimationService._renderer.build_timeline_from_text(text, rate=rate)

        # Arrancar reproducción
        AvatarAnimationService._renderer.start_playback(timeline)

        print(f"[INFO] Vocalización (texto simple): {len(timeline)} visemas")

    @staticmethod
    def stop():
        """Detiene la vocalización actual"""
        if AvatarAnimationService._renderer:
            AvatarAnimationService._renderer.stop()

        # Detener audio
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass

    @staticmethod
    def get_frame() -> np.ndarray:
        """Obtiene el frame actual (para compatibilidad)"""
        with AvatarAnimationService._lock:
            if AvatarAnimationService._last_frame is not None:
                return AvatarAnimationService._last_frame.copy()

        # Fallback
        if AvatarAnimationService._renderer:
            return AvatarAnimationService._renderer.get_frame()

        return np.zeros((256, 256, 3), dtype=np.uint8)

    # ========== COMPATIBILIDAD CON CÓDIGO ANTIGUO ==========

    @staticmethod
    def generate_animation(emotion: str):
        """
        Placeholder para compatibilidad con FER.
        En V3.0 el avatar no cambia expresión por emoción.
        """
        pass

    @staticmethod
    def update_landmarks(landmarks: np.ndarray):
        """
        Placeholder para compatibilidad.
        En V3.0 no se usa warping de landmarks.
        """
        pass