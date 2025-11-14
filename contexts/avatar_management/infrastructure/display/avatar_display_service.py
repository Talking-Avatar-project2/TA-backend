# contexts/avatar_management/infrastructure/display/avatar_display_service.py
import threading
from typing import Optional

import pygame
import numpy as np
import cv2

class AvatarDisplayService:
    """
    Servicio de Pygame en **un solo proceso**.
    - initialize(): crea la ventana (llamar UNA sola vez, en el hilo principal).
    - show_frame(frame): entrega el último frame a presentar.
    - pump(): procesa eventos y dibuja el último frame (llamar periódicamente).
    """
    _initialized = False
    _running = False
    _lock = threading.RLock()
    _last_frame: Optional[np.ndarray] = None
    _screen = None
    _clock = None
    _size = (900, 700)   # ventana
    _surf_rect = None

    @staticmethod
    def initialize():
        if AvatarDisplayService._initialized:
            return
        pygame.init()
        AvatarDisplayService._screen = pygame.display.set_mode(AvatarDisplayService._size)
        pygame.display.set_caption("Avatar Animation")
        AvatarDisplayService._clock = pygame.time.Clock()
        AvatarDisplayService._running = True
        AvatarDisplayService._initialized = True
        print("[INFO] AvatarDisplayService inicializado (proceso único).")

    @staticmethod
    def show_frame(frame_bgr: np.ndarray):
        if not AvatarDisplayService._initialized or frame_bgr is None:
            return
        with AvatarDisplayService._lock:
            AvatarDisplayService._last_frame = frame_bgr.copy()

    @staticmethod
    def pump():
        """
        Procesa eventos y dibuja el último frame.
        Debe llamarse en un bucle del hilo principal (p.ej., app.py).
        """
        if not AvatarDisplayService._initialized:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                AvatarDisplayService._running = False

        bg = pygame.Surface(AvatarDisplayService._size)
        bg.fill((20, 20, 20))
        AvatarDisplayService._screen.blit(bg, (0, 0))

        frame = None
        with AvatarDisplayService._lock:
            if AvatarDisplayService._last_frame is not None:
                frame = AvatarDisplayService._last_frame

        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(np.rot90(rgb))
            # pinta centrado con un margen
            win_w, win_h = AvatarDisplayService._size
            target_h = int(win_h * 0.75)
            aspect = rgb.shape[1] / rgb.shape[0]
            target_w = int(target_h * aspect)
            surf = pygame.transform.smoothscale(surf, (target_w, target_h))
            x = (win_w - target_w) // 2
            y = (win_h - target_h) // 2
            AvatarDisplayService._screen.blit(surf, (x, y))

        pygame.display.flip()
        AvatarDisplayService._clock.tick(60)
