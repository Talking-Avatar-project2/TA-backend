# contexts/avatar_management/application/use_cases/speak_text_use_case.py
from typing import Dict, List, Any, Tuple
from contexts.avatar_management.infrastructure.adapters.tts_adapter import TTSAdapter
from contexts.avatar_management.domain.services.viseme_mapping_service import VisemeMappingService
from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService


class SpeakTextUseCase:
    """
    Caso de uso para vocalización con timeline sincronizado.
    """

    @staticmethod
    def execute(text: str) -> Dict[str, Any]:
        """
        Ejecuta la vocalización completa.

        Pipeline:
        1. Genera timeline desde TTS (con duración real del audio)
        2. Convierte fonemas → visemas
        3. Reproduce audio + visemas sincronizados
        """
        if not isinstance(text, str) or not text.strip():
            return {"success": False, "error": "Texto vacío"}

        try:
            print(f"[SPEAK] Iniciando: '{text[:50]}...'", flush=True)

            # 1. GENERAR TIMELINE DESDE TTS
            tts_result = TTSAdapter.synth_with_timestamps(text)
            phonemes: List[Dict[str, Any]] = tts_result.get("phonemes", [])
            audio_path = tts_result.get("audio_path")

            if not phonemes:
                return {"success": False, "error": "No se generaron fonemas"}

            print(f"[SPEAK] Phonemes generados: {len(phonemes)}", flush=True)

            # 2. CONVERTIR FONEMAS → TIMELINE DE VISEMAS
            # Formato: [(viseme, t_start_sec, t_end_sec), ...]
            timeline = SpeakTextUseCase._phonemes_to_timeline(phonemes)

            if not timeline:
                return {"success": False, "error": "Timeline vacío"}

            print(f"[SPEAK] Timeline generado: {len(timeline)} visemas", flush=True)

            # 3. REPRODUCIR CON ATLASRENDERER
            AvatarAnimationService.speak_with_timeline(timeline, audio_path=audio_path)

            print("[SPEAK] Vocalización iniciada correctamente", flush=True)
            return {"success": True, "message": "Speech iniciado"}

        except Exception as e:
            print(f"[ERROR] SpeakTextUseCase: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    @staticmethod
    def _phonemes_to_timeline(phonemes: List[Dict[str, Any]]) -> List[Tuple[str, float, float]]:
        """
        Convierte fonemas [{"p": char, "start": ms, "end": ms}, ...]
        a timeline [(viseme, t_start_sec, t_end_sec), ...]

        El AtlasRenderer espera tiempos en SEGUNDOS.
        """
        timeline = []

        for ph in phonemes:
            p = str(ph.get("p", "")).strip().lower()
            start_ms = int(ph.get("start", 0))
            end_ms = int(ph.get("end", start_ms + 80))

            # Convertir a segundos
            t_start = start_ms / 1000.0
            t_end = end_ms / 1000.0

            # Mapear fonema → visema
            viseme = VisemeMappingService.map_phoneme(p)

            # Formato que espera AtlasRenderer: (viseme_name, t_start, t_end)
            timeline.append((viseme.upper(), t_start, t_end))

        return timeline