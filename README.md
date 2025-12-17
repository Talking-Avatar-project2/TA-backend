# TA-backend — Backend en Flask

Backend en Python/Flask para la aplicación de soporte emocional con avatar conversacional. Este repositorio expone una API REST organizada por contextos, integra sesión de avatar (LiveAvatar), reconocimiento de expresiones faciales (FER + MediaPipe) y módulos de usuario/perfil basados en Firebase.

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
- Python 3.11, Flask (Blueprints)
- Firebase Admin: Firestore / Storage / Auth
- LiveAvatar API
- MediaPipe + FER
- Ollama (módulo de chatbot)

---

## Manual de usuario (Backend)
El procedimiento detallado para instalar y ejecutar el backend está en el **Manual de usuario**, sección **Backend (1.1.\*)**.

Recomendación de organización dentro del repo:
- `docs/manual_backend.md` (convertido a Markdown), o
- `docs/Manual_de_usuario_Backend.docx` (si prefieres mantenerlo en Word)

---

## Puesta en marcha rápida
> Para instrucciones completas, usa el manual. Esto es un resumen.

### 1) Requisitos
- Python 3.11
- pip
- Git
- (Opcional) Conda

### 2) Instalar dependencias
- Crear/activar entorno virtual
- `pip install -r requirements.txt`

### 3) Variables de entorno
Configurar variables en `.env` (o exportarlas en el sistema). Incluye:
- Credenciales/ruta de Firebase
- Claves de LiveAvatar
- Configuración de ejecución (debug, URL de base de datos)

### 4) Ejecutar
- `python app.py`

---

## Endpoints de referencia
- Salud/estado del servicio (según implementación)
- `/avatar/*`, `/recognition/*`, `/chatbot/*`, `/auth/*`, `/profile/*`

---

## Testing
No se incluyó suite de pruebas automatizadas en esta versión del proyecto.
