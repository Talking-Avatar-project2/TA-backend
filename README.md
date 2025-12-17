# TA-backend (Tesis) — Backend en Flask

Backend en Python/Flask para la aplicación de soporte emocional con avatar conversacional. Este repositorio expone una API REST organizada por contextos, integra sesión de avatar (LiveAvatar), reconocimiento de expresiones faciales en tiempo real (FER + MediaPipe) y módulos de usuario/perfil basados en Firebase.

> El frontend Flutter se encuentra en un repositorio separado: **TA-ui**.

---

## Arquitectura
- **Monolito modular** organizado por **Bounded Contexts** bajo principios de **Domain-Driven Design (DDD)**.
- **Arquitectura en n-capas** orientadas al dominio (Presentación, Aplicación, Dominio, Infraestructura).
- Diseño guiado por **ADD v3 (Attribute-Driven Design)**, priorizando atributos de calidad por iteraciones.

---

## Módulos (Blueprints / Contextos)
- **/avatar**: integración con LiveAvatar. Gestión completa del ciclo de sesión (token, start, stop, keep-alive), recursos (avatares, voces, contextos) y construcción del payload `avatar.speak_text` para que el frontend ordene al avatar hablar.
- **/recognition**: reconocimiento emocional en tiempo real. Endpoint `/recognize` (imagen → emoción + confianza), streaming/estado y sesiones FER con estadísticas por emoción.
- **/chatbot**: lógica conversacional (implementación open-source con Ollama), historial y persistencia de mensajes/transcripciones.
- **/auth**: autenticación mediante Firebase (validación de token y endpoints protegidos).
- **/profile**: gestión de perfil y foto (subida/eliminación) con Firebase Storage.

---

## Tecnologías principales
- Python 3.11
- Flask (Blueprints)
- Firebase Admin (Firestore, Storage, Auth)
- LiveAvatar API
- MediaPipe + FER
- Ollama (módulo de chatbot)

---

## Manual de usuario
El manual de usuario del backend se encuentra en el archivo:

docs/Manual_de_usuario_Backend.docx

---

## Instalación y ejecución

### Requisitos
- Python 3.11
- pip
- Git

### Clonar el repositorio
seleccionar la rama feature/core-v8
git clone <URL_DEL_REPOSITORIO>
cd <CARPETA_DEL_REPOSITORIO>

### Crear y activar entorno virtual (venv)
Crear:
python -m venv .venv

Activar en Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

Activar en Linux/macOS:
source .venv/bin/activate

### Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

### Configurar variables de entorno
Crear un archivo `.env` en la raíz del repositorio con, como mínimo:

LIVEAVATAR_API_KEY=...
OPENAI_API_KEY=...
FLASK_DEBUG=1
DATABASE_URL=...
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

Colocar el archivo de credenciales de Firebase en la raíz del repositorio con el nombre:

firebase-credentials.json

### Ejecutar el servidor
python app.py

El backend queda disponible en:
http://127.0.0.1:5000

---

## Endpoints de referencia
- /avatar/*
- /recognition/*
- /chatbot/*
- /auth/*
- /profile/*

---

## Testing
Esta versión del proyecto no incluye pruebas automatizadas.
