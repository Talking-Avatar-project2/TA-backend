# contexts/avatar_management/application/use_cases/speak_text_use_case.py
"""
Use case mínimo: validar texto y construir payload para frontend (LiveKit data).
Devuelve dict con la estructura que el frontend debe enviar por Data Channel:
{
  "event": "avatar.speak_text",
  "data": {"text": "Hola mundo"}
}
"""
import html
import time

class SpeakTextUseCase:
    @staticmethod
    def execute(text: str, user_id: str = "anonymous"):
        cleaned = text.strip()
        # minimal sanitation: escape to avoid injection in UIs
        safe_text = html.escape(cleaned)
        timestamp = int(time.time() * 1000)
        payload = {
            "event": "avatar.speak_text",
            "meta": {"user_id": user_id, "ts": timestamp},
            "data": {"text": safe_text}
        }
        return payload
