# contexts/avatar_management/infrastructure/adapters/liveavatar_client.py
"""
Cliente HTTP para la API pública de LiveAvatar.
Implementa los endpoints listados por el usuario:
- /v1/sessions/token
- /v1/sessions/start
- /v1/sessions/stop
- /v1/sessions/keep-alive
- /v1/avatars/public
- /v1/avatars/{avatar_id}
- /v1/contexts (CRUD)
- /v1/voices (list/get)
"""
import os
import requests
from typing import Dict, Any, Optional

# Importa la configuración global (ajusta la ruta si tu config está en otro sitio)
try:
    from config import Config
    LIVEAVATAR_API_URL = getattr(Config, "LIVEAVATAR_API_URL", None) or os.getenv("LIVEAVATAR_API_URL", "https://api.liveavatar.com/v1")
    API_KEY = getattr(Config, "LIVEAVATAR_API_KEY", None) or os.getenv("LIVEAVATAR_API_KEY")
except Exception:
    LIVEAVATAR_API_URL = os.getenv("LIVEAVATAR_API_URL", "https://api.liveavatar.com/v1")
    API_KEY = os.getenv("LIVEAVATAR_API_KEY")

class LiveAvatarClientError(Exception):
    pass

class LiveAvatarClient:
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key or API_KEY
        self.api_url = api_url or LIVEAVATAR_API_URL
        self.timeout = timeout
        if not self.api_key:
            raise LiveAvatarClientError("Missing LIVEAVATAR_API_KEY (env LIVEAVATAR_API_KEY)")

    def _headers(self, extra: Dict[str,str]=None):
        h = {
            "accept": "application/json",
            "X-API-KEY": self.api_key,  # según doc, token header es X-API-KEY para token creation
            "Content-Type": "application/json"
        }
        if extra:
            h.update(extra)
        return h

    # --- Sessions ---
    def create_session_token(self, payload: Dict[str,Any]) -> Dict[str,Any]:
        url = f"{self.api_url}/sessions/token"
        r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"create_session_token failed: {r.status_code} {r.text}")
        return r.json()

    def start_session(self, session_token: str) -> Dict[str,Any]:
        url = f"{self.api_url}/sessions/start"
        headers = {"authorization": f"Bearer {session_token}", "accept": "application/json"}
        r = requests.post(url, json={}, headers=headers, timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"start_session failed: {r.status_code} {r.text}")
        return r.json()

    def stop_session(self, session_token: str) -> Dict[str,Any]:
        url = f"{self.api_url}/sessions/stop"
        headers = {"authorization": f"Bearer {session_token}", "accept": "application/json"}
        r = requests.post(url, json={}, headers=headers, timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"stop_session failed: {r.status_code} {r.text}")
        return r.json()

    def keep_alive(self, session_token: str) -> Dict[str,Any]:
        url = f"{self.api_url}/sessions/keep-alive"
        headers = {"authorization": f"Bearer {session_token}", "accept": "application/json"}
        r = requests.post(url, json={}, headers=headers, timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"keep_alive failed: {r.status_code} {r.text}")
        return r.json()

    # --- Avatars ---
    def list_public_avatars(self, params: Dict[str,Any]=None) -> Dict[str,Any]:
        url = f"{self.api_url}/avatars/public"
        r = requests.get(url, params=params or {}, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"list_public_avatars failed: {r.status_code} {r.text}")
        return r.json()

    def get_avatar_by_id(self, avatar_id: str) -> Dict[str,Any]:
        url = f"{self.api_url}/avatars/{avatar_id}"
        r = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"get_avatar_by_id failed: {r.status_code} {r.text}")
        return r.json()

    # --- Contexts CRUD ---
    def create_context(self, payload: Dict[str,Any]) -> Dict[str,Any]:
        url = f"{self.api_url}/contexts"
        r = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"create_context failed: {r.status_code} {r.text}")
        return r.json()

    def list_contexts(self, params: Dict[str,Any]=None) -> Dict[str,Any]:
        url = f"{self.api_url}/contexts"
        r = requests.get(url, params=params or {}, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"list_contexts failed: {r.status_code} {r.text}")
        return r.json()

    def get_context(self, context_id: str) -> Dict[str,Any]:
        url = f"{self.api_url}/contexts/{context_id}"
        r = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"get_context failed: {r.status_code} {r.text}")
        return r.json()

    def update_context(self, context_id: str, payload: Dict[str,Any]) -> Dict[str,Any]:
        url = f"{self.api_url}/contexts/{context_id}"
        r = requests.patch(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"update_context failed: {r.status_code} {r.text}")
        return r.json()

    def delete_context(self, context_id: str) -> Dict[str,Any]:
        url = f"{self.api_url}/contexts/{context_id}"
        r = requests.delete(url, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"delete_context failed: {r.status_code} {r.text}")
        return r.json()

    # --- Voices ---
    def list_voices(self, params: Dict[str,Any]=None) -> Dict[str,Any]:
        url = f"{self.api_url}/voices"
        r = requests.get(url, params=params or {}, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"list_voices failed: {r.status_code} {r.text}")
        return r.json()

    def get_voice_by_id(self, voice_id: str) -> Dict[str,Any]:
        url = f"{self.api_url}/voices/{voice_id}"
        r = requests.get(url, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise LiveAvatarClientError(f"get_voice_by_id failed: {r.status_code} {r.text}")
        return r.json()
