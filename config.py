from dotenv import load_dotenv
import os
from pathlib import Path

# FORZAR explícitamente la ruta del archivo .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    """Clase de configuración global para el backend."""

    # Cargar la API Key de OpenAI desde el entorno
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Otras configuraciones globales (agregar según necesidad)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

    LIVEAVATAR_API_KEY = os.getenv("LIVEAVATAR_API_KEY")
    LIVEAVATAR_API_URL = os.getenv("LIVEAVATAR_API_URL", "https://api.liveavatar.com/v1")
