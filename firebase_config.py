# firebase_config.py
import firebase_admin
from firebase_admin import credentials, storage
import os
import sys
import io

# Configurar UTF-8 para stdout/stderr en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# Render coloca el archivo secreto aquí:
RENDER_CREDENTIALS_PATH = "/etc/secrets/firebase-credentials.json"

# Localmente seguirás usando el archivo normal
LOCAL_CREDENTIALS_PATH = "firebase-credentials.json"


def initialize_firebase():
    """Inicializa Firebase Admin SDK"""

    if firebase_admin._apps:
        return  # Ya inicializado

    # Detectar si estamos en Render (tienen esta variable interna)
    is_render = os.getenv("RENDER") == "true"

    # Seleccionar ruta correcta
    credentials_path = (
        RENDER_CREDENTIALS_PATH
        if os.path.exists(RENDER_CREDENTIALS_PATH)
        else LOCAL_CREDENTIALS_PATH
    )

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"No se encontró credencial Firebase: {credentials_path}"
        )

    cred = credentials.Certificate(credentials_path)

    storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
    if not storage_bucket:
        raise ValueError(
            "FIREBASE_STORAGE_BUCKET no está configurado en las variables de entorno"
        )

    firebase_admin.initialize_app(cred, {
        "storageBucket": storage_bucket
    })

    print("[OK] Firebase inicializado correctamente en:", credentials_path)


def get_storage_bucket():
    return storage.bucket()
