# contexts/avatar_management/application/use_cases/generate_viseme_sequence_use_case.py
from dataclasses import dataclass
from typing import List, Dict, Any

from contexts.avatar_management.domain.services.viseme_mapping_service import VisemeMappingService

try:
    from phonemizer import phonemize  # opcional
except ImportError:
    phonemize = None
    print("[Warning] phonemizer no instalado. Usa otro adaptador TTS con fonemas temporizados.")


@dataclass
class TimedViseme:
    """
    Representa un visema temporizado. Puede venir de:
    - texto → fonemas → visemas
    - payload de fonemas con timestamps
    - payload directo de visemas

    Campos:
      viseme: etiqueta (p.ej., 'viseme_MBP', 'viseme_AA', etc.)
      start_time: inicio en segundos (relativo a 0)
      duration: duración en segundos
      ratio: intensidad de apertura de labios [0..1] (opcional; si no se define, se infiere por viseme)
    """
    viseme: str
    start_time: float
    duration: float
    ratio: float | None = None


class GenerateVisemeSequenceUseCase:
    """
    Genera una secuencia temporizada de visemas.
    Permite tres entradas:
      1) Texto (requiere 'phonemizer' instalado) → from_text
      2) Fonemas temporizados [{'phoneme','start','duration'}] → from_phoneme_timestamps
      3) Visemas temporizados [{'viseme','start','duration', 'ratio'?}] → from_viseme_payload
    """

    def __init__(self, default_duration: float = 0.15):
        self.default_duration = float(max(0.05, default_duration))

    # --------- Entradas de alto nivel ---------
    def from_text(self, text: str) -> List[TimedViseme]:
        """
        Convierte texto a una lista de visemas temporizados.
        Requiere 'phonemizer'. Si no está, levanta ImportError.
        """
        if phonemize is None:
            raise ImportError("phonemizer no está instalado. Instálalo con: pip install phonemizer")

        if not isinstance(text, str) or not text.strip():
            return []

        # Fonemizar en inglés por defecto (ajusta si tu TTS está en otro idioma)
        phoneme_str = phonemize(text, language='en-us', backend='espeak', strip=True, njobs=1)
        # phonemizer devuelve algo tipo "hh eh l ow  w er l d"
        phonemes = [p for p in phoneme_str.split() if p]

        visemes: List[TimedViseme] = []
        t = 0.0
        for ph in phonemes:
            v = VisemeMappingService.map_phoneme(ph)
            ratio = VisemeMappingService.viseme_ratio(v)
            visemes.append(TimedViseme(viseme=v, start_time=t, duration=self.default_duration, ratio=ratio))
            t += self.default_duration
        return visemes

    def from_phoneme_timestamps(self, items: List[Dict[str, Any]]) -> List[TimedViseme]:
        """
        items: [{"phoneme": "m", "start": 0.00, "duration": 0.12}, ...]
        """
        if not isinstance(items, list):
            return []
        out: List[TimedViseme] = []
        for it in items:
            ph = str(it.get("phoneme", "")).strip().lower()
            if not ph:
                continue
            start = float(it.get("start", it.get("start_time", 0.0)) or 0.0)
            dur = float(it.get("duration", self.default_duration) or self.default_duration)
            v = VisemeMappingService.map_phoneme(ph)
            ratio = VisemeMappingService.viseme_ratio(v)
            out.append(TimedViseme(viseme=v, start_time=start, duration=dur, ratio=ratio))
        out.sort(key=lambda x: x.start_time)
        return out

    def from_viseme_payload(self, items: List[Dict[str, Any]]) -> List[TimedViseme]:
        """
        items: [{"viseme": "viseme_AA", "start": 0.0, "duration": 0.15, "ratio": 0.7?}, ...]
        """
        if not isinstance(items, list):
            return []
        out: List[TimedViseme] = []
        for it in items:
            v = str(it.get("viseme", "")).strip()
            if not v:
                continue
            start = float(it.get("start", it.get("start_time", 0.0)) or 0.0)
            dur = float(it.get("duration", self.default_duration) or self.default_duration)
            ratio = it.get("ratio", None)
            if ratio is None:
                ratio = VisemeMappingService.viseme_ratio(v)
            else:
                ratio = float(max(0.0, min(1.0, float(ratio))))
            out.append(TimedViseme(viseme=v, start_time=start, duration=dur, ratio=ratio))
        out.sort(key=lambda x: x.start_time)
        return out
