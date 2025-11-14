# backend_refactor/test_avatar_talk.py
import requests

# Texto de prueba — puedes editarlo libremente
TEXT = (
    "Hola, soy tu avatar probando la vocalización. "
    "De esta manera sabremos si está funcionando realmente el proceso de ejecución. "
    "Además, vamos a cambiar el modelo de generación de avatar, "
    "a partir de ahora lo trabajaremos a partir de una imagen base "
    "y ya no las ochenta iniciales. Esperemos que funcione como se espera."
)

BACKEND_URL = "http://localhost:5000/avatar/speak-text"

def main():
    print("[INFO] Enviando texto al backend...")
    try:
        response = requests.post(
            BACKEND_URL,
            json={"text": TEXT},
            timeout=30
        )
        print("[INFO] Respuesta del backend:")
        print(response.json())
    except Exception as e:
        print(f"[ERROR] No se pudo conectar con el backend: {e}")

if __name__ == "__main__":
    main()
