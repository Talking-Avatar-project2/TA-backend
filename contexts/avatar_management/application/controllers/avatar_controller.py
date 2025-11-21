# contexts/avatar_management/application/controllers/avatar_controller.py
from flask import Blueprint, request, jsonify, current_app
from contexts.avatar_management.domain.services.liveavatar_service import LiveAvatarService, LiveAvatarClientError
from contexts.recognition_management.domain.services.fer_session_manager import FerSessionManager
from contexts.recognition_management.application.use_cases.emotion_session_save_use_case import EmotionSessionSaveUseCase

avatar_bp = Blueprint("avatar_bp", __name__)

# Inicialización del servicio LiveAvatar cuando Flask procesa la primera request
@avatar_bp.before_app_request
def _init_liveavatar():
    try:
        # Solo inicializar una vez
        if not LiveAvatarService.ready():
            LiveAvatarService.initialize()
    except Exception as e:
        current_app.logger.warning(f"LiveAvatarService init warning: {e}")


# --------- Session endpoints ---------
@avatar_bp.post("/session/token")
def create_session_token():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id", "anonymous")
    mode = payload.get("mode", "FULL")
    avatar_id = payload.get("avatar_id")
    voice_id = payload.get("voice_id")
    language = payload.get("language")
    context_id = payload.get("context_id")   # <--- nuevo
    extra = payload.get("extra")

    try:
        record = LiveAvatarService.create_session_token_for_user(
            user_id,
            mode=mode,
            avatar_id=avatar_id,
            voice_id=voice_id,
            language=language,
            context_id=context_id,   # <--- pasamos context_id
            extra=extra
        )
        return jsonify({"success": True, "session": record}), 201

    except LiveAvatarClientError as e:
        # si la API respondió validación, devolvemos 422 al cliente con la info
        current_app.logger.warning(f"LiveAvatarClientError: {e}")
        return jsonify({"success": False, "error": str(e)}), 422

    except Exception as e:
        current_app.logger.exception("create_session_token failed")
        return jsonify({"success": False, "error": str(e)}), 500



@avatar_bp.post("/session/start")
def start_session():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "anonymous")
    try:
        info = LiveAvatarService.start_session_for_user(user_id)
        # Iniciar FER
        FerSessionManager.start()
        return jsonify({"success": True, "session": info}), 200
    except Exception as e:
        current_app.logger.exception("start_session failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.post("/session/stop")
def stop_session():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "anonymous")
    try:
        resp = LiveAvatarService.stop_session_for_user(user_id)

        FerSessionManager.stop()
        stats = FerSessionManager.get_stats()

        dominant = max(stats, key=stats.get)

        from contexts.recognition_management.application.use_cases.emotion_session_save_use_case import EmotionSessionSaveUseCase
        EmotionSessionSaveUseCase.execute(
            user_id="default_user",
            stats=stats,
            dominant_emotion=dominant
        )

        return jsonify({
            "success": True,
            "result": resp,
            "emotion_stats": stats,
            "dominant_emotion": dominant
        }), 200

    except Exception as e:
        current_app.logger.exception("stop_session failed")
        return jsonify({"success": False, "error": str(e)}), 500



@avatar_bp.post("/session/keep-alive")
def keep_alive():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "anonymous")
    try:
        resp = LiveAvatarService.keep_alive_for_user(user_id)
        return jsonify({"success": True, "result": resp}), 200
    except Exception as e:
        current_app.logger.exception("keep_alive failed")
        return jsonify({"success": False, "error": str(e)}), 500


# --------- Avatars ---------
@avatar_bp.get("/avatars")
def list_avatars():
    try:
        resp = LiveAvatarService.list_public_avatars()
        return jsonify({"success": True, "avatars": resp}), 200
    except Exception as e:
        current_app.logger.exception("list_avatars failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.get("/avatars/<avatar_id>")
def get_avatar(avatar_id):
    try:
        resp = LiveAvatarService.get_avatar_by_id(avatar_id)
        return jsonify({"success": True, "avatar": resp}), 200
    except Exception as e:
        current_app.logger.exception("get_avatar failed")
        return jsonify({"success": False, "error": str(e)}), 500


# --------- Contexts ---------
@avatar_bp.post("/contexts")
def create_context():
    payload = request.get_json(silent=True) or {}
    try:
        resp = LiveAvatarService.create_context(payload)
        return jsonify({"success": True, "context": resp}), 201
    except Exception as e:
        current_app.logger.exception("create_context failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.get("/contexts")
def list_contexts():
    try:
        resp = LiveAvatarService.list_contexts()
        return jsonify({"success": True, "contexts": resp}), 200
    except Exception as e:
        current_app.logger.exception("list_contexts failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.get("/contexts/<context_id>")
def get_context(context_id):
    try:
        resp = LiveAvatarService.get_context(context_id)
        return jsonify({"success": True, "context": resp}), 200
    except Exception as e:
        current_app.logger.exception("get_context failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.patch("/contexts/<context_id>")
def update_context(context_id):
    payload = request.get_json(silent=True) or {}
    try:
        resp = LiveAvatarService.update_context(context_id, payload)
        return jsonify({"success": True, "context": resp}), 200
    except Exception as e:
        current_app.logger.exception("update_context failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.delete("/contexts/<context_id>")
def delete_context(context_id):
    try:
        resp = LiveAvatarService.delete_context(context_id)
        return jsonify({"success": True, "result": resp}), 200
    except Exception as e:
        current_app.logger.exception("delete_context failed")
        return jsonify({"success": False, "error": str(e)}), 500


# --------- Voices ---------
@avatar_bp.get("/voices")
def list_voices():
    try:
        resp = LiveAvatarService.list_voices()
        return jsonify({"success": True, "voices": resp}), 200
    except Exception as e:
        current_app.logger.exception("list_voices failed")
        return jsonify({"success": False, "error": str(e)}), 500


@avatar_bp.get("/voices/<voice_id>")
def get_voice(voice_id):
    try:
        resp = LiveAvatarService.get_voice_by_id(voice_id)
        return jsonify({"success": True, "voice": resp}), 200
    except Exception as e:
        current_app.logger.exception("get_voice failed")
        return jsonify({"success": False, "error": str(e)}), 500


# --------- Speak Text ---------
@avatar_bp.post("/send-text")
def send_text():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "anonymous")
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"success": False, "error": "Texto vacío"}), 400

    from contexts.avatar_management.application.use_cases.speak_text_use_case import SpeakTextUseCase
    payload = SpeakTextUseCase.execute(text=text, user_id=user_id)
    return jsonify({"success": True, "payload_for_client": payload}), 202
