import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """Clase de configuración global para el backend."""

    # Cargar la API Key de OpenAI desde el entorno
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Otras configuraciones globales (agregar según necesidad)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
