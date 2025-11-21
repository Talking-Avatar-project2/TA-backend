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

# Ruta al archivo de credenciales (usa la misma que Firestore)
CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')

def initialize_firebase():
    """Inicializa Firebase Admin SDK"""
    if not firebase_admin._apps:
        # Verificar que existe el archivo de credenciales
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"No se encontró el archivo de credenciales en: {CREDENTIALS_PATH}\n"
                "Descarga las credenciales desde Firebase Console → Configuración → Cuentas de servicio"
            )

        cred = credentials.Certificate(CREDENTIALS_PATH)

        # Obtener el storage bucket desde variables de entorno
        storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
        if not storage_bucket:
            raise ValueError(
                "FIREBASE_STORAGE_BUCKET no está configurado en .env\n"
                "Ejemplo: FIREBASE_STORAGE_BUCKET=tu-project-id.appspot.com"
            )

        firebase_admin.initialize_app(cred, {
            'storageBucket': storage_bucket
        })
        print("[OK] Firebase inicializado correctamente")

def get_storage_bucket():
    """Obtiene el bucket de Storage"""
    return storage.bucket()
