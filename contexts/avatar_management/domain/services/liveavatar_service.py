# contexts/avatar_management/domain/services/liveavatar_service.py
"""
LiveAvatarService - lógica de dominio ligera.
- Mantiene un registro en memoria de sesiones (user_id -> {session_token, session_id, livekit})
- Expone métodos para crear token, start, stop, keep_alive
- Implementa fallback neutral: si no hay credenciales o API falla, responde con 'neutral' info.
"""
import threading
import time
from typing import Dict, Any, Optional

from contexts.avatar_management.infrastructure.adapters.liveavatar_client import LiveAvatarClient, LiveAvatarClientError
import os

DEFAULT_AVATAR_ID = os.getenv("LIVEAVATAR_DEFAULT_AVATAR_ID")
DEFAULT_VOICE_ID = os.getenv("LIVEAVATAR_DEFAULT_VOICE_ID")
DEFAULT_CONTEXT_ID = os.getenv("LIVEAVATAR_DEFAULT_CONTEXT_ID")
DEFAULT_LANGUAGE = os.getenv("LIVEAVATAR_DEFAULT_LANGUAGE", "en")

class LiveAvatarService:
    _client: Optional[LiveAvatarClient] = None
    _sessions: Dict[str, Dict[str,Any]] = {}
    _lock = threading.RLock()
    _initialized = False

    @classmethod
    def initialize(cls, api_key: Optional[str]=None, api_url: Optional[str]=None):
        if cls._initialized:
            return
        try:
            cls._client = LiveAvatarClient(api_key=api_key, api_url=api_url)
            cls._initialized = True
        except Exception as e:
            cls._client = None
            cls._initialized = False
            # no exception fatal; we'll use neutral fallback
            print(f"[LiveAvatarService] initialize failed: {e}")

    @classmethod
    def ready(cls) -> bool:
        return cls._initialized and cls._client is not None

    @classmethod
    def create_session_token_for_user(cls, user_id: str, mode: str = "FULL", avatar_id: Optional[str] = None,
                                      voice_id: Optional[str] = None, language: Optional[str] = None,
                                      context_id: Optional[str] = None, extra: Dict[str, Any] = None):
        """
        Create session token by calling /sessions/token.
        Stores token+meta in memory keyed by user_id.
        """
        with cls._lock:
            # fallback neutral if no client at all
            if not cls._client:
                dummy = {
                    "session_id": None,
                    "session_token": None,
                    "livekit_url": None,
                    "livekit_client_token": None,
                    "mode": "NEUTRAL"
                }
                cls._sessions[user_id] = dummy
                return dummy

            # use provided values or fall back to env defaults
            avatar_id = avatar_id or DEFAULT_AVATAR_ID
            voice_id = voice_id or DEFAULT_VOICE_ID
            context_id = context_id or DEFAULT_CONTEXT_ID
            language = language or DEFAULT_LANGUAGE

            # Validation: mode FULL requires avatar_id, voice_id, context_id
            if mode == "FULL":
                missing = []
                if not avatar_id:
                    missing.append("avatar_id")
                if not voice_id:
                    missing.append("avatar_persona.voice_id")
                if not context_id:
                    missing.append("avatar_persona.context_id")
                if missing:
                    raise LiveAvatarClientError(f"Missing required fields for mode=FULL: {', '.join(missing)}")

            # Payload EXACTO según la doc de LiveAvatar
            payload = {
                "mode": mode,
                "avatar_id": avatar_id,
                "avatar_persona": {
                    "voice_id": voice_id,
                    "context_id": context_id,
                    "language": language
                }
            }

            if extra:
                payload.update(extra)

            # Llamada real a la API de LiveAvatar
            resp = cls._client.create_session_token(payload)

            # La API devuelve algo como:
            # {
            #   "code": 1000,
            #   "data": {
            #       "session_id": "...",
            #       "session_token": "...",
            #   },
            #   "message": "Session token created successfully"
            # }
            data = {}
            if isinstance(resp, dict):
                data = resp.get("data") or {}
            session_id = data.get("session_id")
            session_token = data.get("session_token")

            record = {
                "session_id": session_id,
                "session_token": session_token,
                "raw": resp,
                "mode": mode
            }
            cls._sessions[user_id] = record
            return record


    @classmethod
    def start_session_for_user(cls, user_id: str):
        with cls._lock:
            info = cls._sessions.get(user_id)
            if not info:
                raise LiveAvatarClientError("no session token found; call create_session_token first")
            token = info.get("session_token")
            if not token:
                # neutral fallback
                return {"mode":"NEUTRAL", "message":"no token; neutral fallback"}
            resp = cls._client.start_session(token)
            # response typically contains livekit info
            info.update({"start_response": resp})
            return info

    @classmethod
    def stop_session_for_user(cls, user_id: str):
        with cls._lock:
            info = cls._sessions.get(user_id)
            if not info:
                return {"status":"no-session"}
            token = info.get("session_token")
            if token and cls._client:
                resp = cls._client.stop_session(token)
            else:
                resp = {"status":"neutral-stopped"}
            # remove from registry
            cls._sessions.pop(user_id, None)
            return resp

    @classmethod
    def keep_alive_for_user(cls, user_id: str):
        with cls._lock:
            info = cls._sessions.get(user_id)
            if not info:
                return {"status":"no-session"}
            token = info.get("session_token")
            if token and cls._client:
                resp = cls._client.keep_alive(token)
                return resp
            return {"status":"neutral"}

    # --- helpers to expose avatars/contexts/voices --- #
    @classmethod
    def list_public_avatars(cls, params: Dict[str,Any]=None):
        if not cls._client:
            return {"avatars": [], "note":"neutral-fallback"}
        return cls._client.list_public_avatars(params=params)

    @classmethod
    def get_avatar_by_id(cls, avatar_id: str):
        if not cls._client:
            return {"avatar": None, "note":"neutral-fallback"}
        return cls._client.get_avatar_by_id(avatar_id)

    @classmethod
    def create_context(cls, payload: Dict[str,Any]):
        if not cls._client:
            raise LiveAvatarClientError("not configured")
        return cls._client.create_context(payload)

    @classmethod
    def list_contexts(cls, params: Dict[str,Any]=None):
        if not cls._client:
            return {"contexts": [], "note":"neutral-fallback"}
        return cls._client.list_contexts(params=params)

    @classmethod
    def get_context(cls, context_id: str):
        if not cls._client:
            return {"context": None, "note":"neutral-fallback"}
        return cls._client.get_context(context_id)

    @classmethod
    def update_context(cls, context_id: str, payload: Dict[str,Any]):
        if not cls._client:
            raise LiveAvatarClientError("not configured")
        return cls._client.update_context(context_id, payload)

    @classmethod
    def delete_context(cls, context_id: str):
        if not cls._client:
            raise LiveAvatarClientError("not configured")
        return cls._client.delete_context(context_id)

    @classmethod
    def list_voices(cls, params: Dict[str,Any]=None):
        if not cls._client:
            return {"voices": [], "note":"neutral-fallback"}
        return cls._client.list_voices(params=params)

    @classmethod
    def get_voice_by_id(cls, voice_id: str):
        if not cls._client:
            return {"voice": None, "note":"neutral-fallback"}
        return cls._client.get_voice_by_id(voice_id)
