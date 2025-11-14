# contexts/avatar_management/infrastructure/adapters/tts_adapter.py
import os
import wave
import re
import numpy as np
from typing import Dict, List, Any, Optional


class TTSAdapter:
    """
    Adaptador TTS con análisis de audio para sincronización precisa.
    Detecta silencios y pausas en el audio real.
    """

    @staticmethod
    def synth_with_timestamps(text: str, wpm: int = 160, audio_path: str | None = None) -> dict:
        """
        Genera timeline sincronizado con SILENCIOS del audio real.
        """
        text = (text or "").strip()
        if not text:
            return {"phonemes": [], "audio_path": None}

        # 1. Resolver audio
        chosen_audio = TTSAdapter._resolve_audio_path(audio_path)

        # 2. Analizar audio (detectar silencios)
        audio_segments = TTSAdapter._analyze_audio_segments(chosen_audio)

        if not audio_segments:
            # Fallback: distribución uniforme
            print("[WARN] No se pudo analizar audio, usando distribución uniforme")
            return TTSAdapter._fallback_uniform_distribution(text, chosen_audio)

        # 3. Tokenizar texto
        tokens = TTSAdapter._tokenize_text(text)

        # 4. Distribuir tokens en los segmentos CON VOZ
        phonemes = TTSAdapter._distribute_with_silence_detection(tokens, audio_segments)

        total_ms = int(phonemes[-1]["end"]) if phonemes else 0
        print(f"[TTS] Timeline generado: {len(phonemes)} fonemas en {total_ms}ms (con silencios detectados)")

        return {
            "phonemes": phonemes,
            "audio_path": chosen_audio
        }

    @staticmethod
    def _analyze_audio_segments(audio_path: Optional[str]) -> List[Dict[str, Any]]:
        """
        Analiza el audio y devuelve segmentos [voice, silence, voice, ...]
        """
        if not audio_path or not os.path.isfile(audio_path):
            return []

        try:
            # Leer audio como numpy array
            with wave.open(audio_path, "rb") as wf:
                sample_rate = wf.getframerate()
                n_frames = wf.getnframes()
                audio_data = wf.readframes(n_frames)

                # Convertir a numpy array (int16)
                audio_np = np.frombuffer(audio_data, dtype=np.int16)

                # Si es estéreo, convertir a mono
                n_channels = wf.getnchannels()
                if n_channels == 2:
                    audio_np = audio_np.reshape(-1, 2).mean(axis=1).astype(np.int16)

            # Calcular energía (RMS) en ventanas de 50ms
            window_ms = 50
            window_samples = int(sample_rate * window_ms / 1000)

            # Umbral de silencio (ajustable)
            silence_threshold = 800

            segments = []
            current_type = None
            current_start = 0

            for i in range(0, len(audio_np), window_samples):
                chunk = audio_np[i:i + window_samples]

                # Calcular energía RMS
                rms = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))

                # Clasificar como voz o silencio
                is_silence = rms < silence_threshold
                segment_type = "silence" if is_silence else "voice"

                # Cambio de segmento
                if segment_type != current_type:
                    if current_type is not None:
                        end_ms = int((i / sample_rate) * 1000)
                        segments.append({
                            "type": current_type,
                            "start_ms": current_start,
                            "end_ms": end_ms
                        })
                    current_type = segment_type
                    current_start = int((i / sample_rate) * 1000)

            # Último segmento
            if current_type:
                end_ms = int((len(audio_np) / sample_rate) * 1000)
                segments.append({
                    "type": current_type,
                    "start_ms": current_start,
                    "end_ms": end_ms
                })

            # Fusionar segmentos muy cortos
            segments = TTSAdapter._merge_short_segments(segments, min_duration_ms=100)

            print(f"[TTS] Detectados {len(segments)} segmentos de audio:", flush=True)
            for seg in segments:
                duration = seg["end_ms"] - seg["start_ms"]
                print(f"  - {seg['type']:8s} {seg['start_ms']:5d}ms → {seg['end_ms']:5d}ms ({duration}ms)")

            return segments

        except Exception as e:
            print(f"[ERROR] Análisis de audio falló: {e}")
            return []

    @staticmethod
    def _merge_short_segments(segments: List[Dict], min_duration_ms: int) -> List[Dict]:
        """Fusiona segmentos muy cortos con sus vecinos"""
        if not segments:
            return []

        merged = [segments[0]]

        for seg in segments[1:]:
            last = merged[-1]
            duration = seg["end_ms"] - seg["start_ms"]

            if duration < min_duration_ms:
                last["end_ms"] = seg["end_ms"]
                # Mantener el tipo del segmento más largo
                if (seg["end_ms"] - seg["start_ms"]) > (last["end_ms"] - last["start_ms"]):
                    last["type"] = seg["type"]
            else:
                merged.append(seg)

        return merged

    @staticmethod
    def _distribute_with_silence_detection(tokens: List[Dict], segments: List[Dict]) -> List[Dict[str, Any]]:
        """
        Distribuye tokens SOLO en segmentos de voz, inserta REST en silencios.
        VERSIÓN CORREGIDA: Distribuye TODOS los tokens correctamente.
        """
        phonemes = []

        # Extraer TODOS los caracteres del texto
        all_chars = []
        for token in tokens:
            if token["type"] == "word":
                all_chars.extend(token["chars"])
            elif token["type"] == "pause":
                all_chars.append(" ")  # representa la pausa

        if not all_chars:
            return []

        # Calcular tiempo total de VOZ disponible
        total_voice_ms = sum(seg["end_ms"] - seg["start_ms"] for seg in segments if seg["type"] == "voice")

        if total_voice_ms == 0:
            return []

        # Tiempo por carácter en segmentos de voz
        ms_per_char = total_voice_ms / len(all_chars)

        print(
            f"[TTS] Distribuyendo {len(all_chars)} caracteres en {total_voice_ms}ms de voz ({ms_per_char:.1f}ms/char)")

        # ALGORITMO CORREGIDO: Distribuir caracteres secuencialmente
        char_idx = 0

        for seg in segments:
            seg_start = seg["start_ms"]
            seg_end = seg["end_ms"]
            seg_type = seg["type"]
            seg_duration = seg_end - seg_start

            if seg_type == "silence":
                # Insertar REST por todo el silencio
                phonemes.append({
                    "p": " ",
                    "start": seg_start,
                    "end": seg_end
                })
                print(f"[TTS]   Silencio: {seg_start}ms → {seg_end}ms")

            elif seg_type == "voice":
                # Calcular cuántos caracteres caben en este segmento
                chars_in_segment = int(seg_duration / ms_per_char)

                # Ajustar si nos pasamos del total
                chars_in_segment = min(chars_in_segment, len(all_chars) - char_idx)

                print(f"[TTS]   Voz: {seg_start}ms → {seg_end}ms ({chars_in_segment} chars)")

                # Distribuir caracteres en este segmento
                current_ms = seg_start

                for i in range(chars_in_segment):
                    if char_idx >= len(all_chars):
                        break

                    char = all_chars[char_idx]

                    # Calcular duración de este carácter
                    char_duration = ms_per_char

                    # Asegurar que no nos salgamos del segmento
                    if current_ms + char_duration > seg_end:
                        char_duration = seg_end - current_ms

                    phonemes.append({
                        "p": char,
                        "start": int(current_ms),
                        "end": int(current_ms + char_duration)
                    })

                    current_ms += char_duration
                    char_idx += 1

        # Si quedan caracteres sin asignar (error de cálculo), distribuirlos uniformemente en el último segmento de voz
        if char_idx < len(all_chars):
            print(f"[WARN] Quedan {len(all_chars) - char_idx} caracteres sin asignar")

            # Buscar el último segmento de voz
            last_voice_seg = next((seg for seg in reversed(segments) if seg["type"] == "voice"), None)

            if last_voice_seg:
                remaining_chars = all_chars[char_idx:]
                seg_start = last_voice_seg["start_ms"]
                seg_end = last_voice_seg["end_ms"]
                seg_duration = seg_end - seg_start

                char_duration = seg_duration / len(remaining_chars)
                current_ms = seg_start

                for char in remaining_chars:
                    phonemes.append({
                        "p": char,
                        "start": int(current_ms),
                        "end": int(current_ms + char_duration)
                    })
                    current_ms += char_duration

        return phonemes

    @staticmethod
    def _fallback_uniform_distribution(text: str, audio_path: Optional[str]) -> dict:
        """Distribución uniforme (fallback si el análisis falla)"""
        audio_duration_ms = TTSAdapter._get_audio_duration_ms(audio_path)
        if not audio_duration_ms:
            audio_duration_ms = 5000

        chars = [c.lower() for c in text if c.strip()]
        n = max(1, len(chars))
        slot_ms = audio_duration_ms // n

        phonemes = []
        cur = 0
        for c in chars:
            phonemes.append({"p": c, "start": cur, "end": cur + slot_ms})
            cur += slot_ms

        return {"phonemes": phonemes, "audio_path": audio_path}

    @staticmethod
    def _resolve_audio_path(audio_path: Optional[str]) -> Optional[str]:
        """Determina qué audio usar"""
        if audio_path and os.path.isfile(audio_path):
            return audio_path

        default_path = os.path.join("audios", "test_avatar_talk.wav")
        if os.path.isfile(default_path):
            return default_path

        return None

    @staticmethod
    def _get_audio_duration_ms(audio_path: Optional[str]) -> Optional[int]:
        """Lee duración del WAV"""
        if not audio_path or not os.path.isfile(audio_path):
            return None

        try:
            with wave.open(audio_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return int((frames / rate) * 1000)
        except Exception:
            return None

    @staticmethod
    def _tokenize_text(text: str) -> List[Dict[str, Any]]:
        """Tokeniza texto en palabras y pausas"""
        PAUSE_FACTORS = {",": 1.5, ";": 2.0, ".": 2.5, "!": 2.5, "?": 2.5, ":": 2.0}

        tokens = []
        parts = re.findall(r'\w+|[^\w\s]', text)

        for part in parts:
            if part in PAUSE_FACTORS:
                tokens.append({"type": "pause", "duration_factor": PAUSE_FACTORS[part]})
            elif part.strip():
                chars = [c.lower() for c in part if c.isalnum()]
                if chars:
                    tokens.append({"type": "word", "chars": chars})

        return tokens