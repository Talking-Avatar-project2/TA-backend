# contexts/avatar_management/application/controllers/avatar_controller.py
from flask import Blueprint, jsonify, request
import threading
from contexts.avatar_management.application.use_cases.speak_text_use_case import SpeakTextUseCase

avatar_bp = Blueprint("avatar_bp", __name__)


@avatar_bp.route("/speak-text", methods=["POST"])
def speak_text():
    """
    Endpoint para vocalización sincronizada.
    CORREGIDO: Audio y visemas se sincronizan correctamente.
    """
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    wpm = int(data.get("wpm", 160))

    if not text:
        return jsonify({"error": "Texto vacío"}), 400

    # Lanzar en thread para no bloquear Flask
    def _run_speech():
        try:
            # SpeakTextUseCase maneja TODO: audio + visemas sincronizados
            result = SpeakTextUseCase.execute(text)

            if not result.get("success"):
                print(f"[ERROR] SpeakTextUseCase falló: {result.get('error')}", flush=True)
        except Exception as e:
            print(f"[ERROR] speak_text thread: {e}", flush=True)
            import traceback
            traceback.print_exc()

    threading.Thread(target=_run_speech, daemon=True).start()

    return jsonify({"status": "accepted", "message": "Vocalización iniciada"}), 202


@avatar_bp.post("/stop")
def stop():
    """Detiene la vocalización actual"""
    try:
        from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService
        AvatarAnimationService.stop()
        return jsonify({"status": "stopped"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500