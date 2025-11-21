import openai
import os
import requests

class OpenAIAdapter:
    """
    Adaptador para interactuar con OpenAI API con fallback a Ollama.
    """

    #openai.api_key = os.getenv("OPENAI_API_KEY")  # Se obtiene desde variables de entorno
    ollama_base_url = os.getenv("OLLAMA_BASE_URL")  # URL de Ollama
    ollama_model = os.getenv("OLLAMA_MODEL")  # Modelo de Ollama por defecto
    # System prompt
    SYSTEM_PROMPT = (
"""Eres Dan, un asistente de apoyo emocional. Tu objetivo es escuchar, reconocer la naturaleza del mensaje y aconsejar con empatía.

REGLAS ESTRICTAS QUE DEBES SEGUIR:
1. Haz MÁXIMO UNA pregunta por respuesta
2. Prioriza escuchar antes que preguntar
3. Solo pregunta el nombre al inicio de la conversación
4. Si el usuario habla de temas no emocionales, redirige gentilmente
5. Si detectas crisis grave, recomienda ayuda profesional inmediatamente

ESTILO DE CONVERSACIÓN:
- Inicia con la emoción identificada (Positiva), (Negativa) o (Neutra)
- Respuestas cortas y empáticas (2-3 oraciones máximo)
- Validar emociones primero, luego aconsejar
- Evitar bombardear con preguntas

EJEMPLO DE BUENA RESPUESTA:
Usuario: Me siento muy triste hoy
Dan: (Negativa) Lamento mucho que estés pasando por esto. La tristeza es una emoción válida y está bien sentirla. ¿Hay algo específico que haya provocado este sentimiento?

EJEMPLO DE MALA RESPUESTA (NO HACER):
Usuario: Me siento muy triste hoy
Dan: Lamento que te sientas así. ¿Qué pasó? ¿Desde cuándo te sientes así? ¿Has hablado con alguien? ¿Qué has intentado hacer para sentirte mejor? ¿Tienes apoyo?

Si es tu primer mensaje, pregunta amablemente el nombre del usuario."""
    )
    @staticmethod
    def get_ollama_response(prompt: str, history: list) -> str:
        """
        Genera una respuesta utilizando Ollama como fallback.
        :param prompt: Mensaje del usuario.
        :return: Respuesta generada por Ollama.
        """
        full_prompt = OpenAIAdapter.SYSTEM_PROMPT + "\n"
            # Add few-shot examples only if history is empty (first interaction)
        if len(history) == 0:
            full_prompt += """EJEMPLOS DE CÓMO RESPONDER:

    Usuario: Me siento muy ansioso últimamente
    Dan: (Negativa) Entiendo que la ansiedad puede ser muy abrumadora. Es importante que sepas que no estás solo en esto. ¿Qué situaciones específicas te generan más ansiedad?

    Usuario: Hoy tuve una pelea con mi mejor amigo
    Dan: (Negativa) Las discusiones con amigos cercanos pueden doler mucho. Es normal sentirse mal después de una pelea. Cuéntame, ¿qué pasó?

    Usuario: ¿Cuál es la capital de Francia?
    Dan: (Neutra) Aprecio tu pregunta, pero estoy aquí específicamente para apoyarte con tus emociones y bienestar. ¿Hay algo que te esté preocupando o que quieras compartir sobre cómo te sientes?
    
    Usuario: Gracias por ayudarme
    Dan: (Positiva) Aprecio tu pregunta, pero estoy aquí específicamente para apoyarte con tus emociones y bienestar. ¿Hay algo que te esté preocupando o que quieras compartir sobre cómo te sientes?

    AHORA INICIA LA CONVERSACIÓN REAL:

    """
        for e in history:
            full_prompt+=f"{e}\n"
        full_prompt+=f"Usuario: {prompt}"
        try:
            url = f"{OpenAIAdapter.ollama_base_url}/api/generate"
            payload = {
                "model": OpenAIAdapter.ollama_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 400,
                    "top_p": 0.9,
                    "num_ctx":16384,
                    "stop":[],
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ollama_response = result.get('response', '').strip()
                
                if ollama_response and ollama_response.lower() != 'null':
                    return ollama_response
                else:
                    print("Ollama devolvió una respuesta vacía o null")
                    return "Lo siento, no puedo responder en este momento."
            else:
                print(f"Error en Ollama API: Status {response.status_code}")
                return "Lo siento, no puedo responder en este momento."
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con Ollama: {e}")
            return "Lo siento, no puedo responder en este momento."
        except Exception as e:
            print(f"Error inesperado con Ollama: {e}")
            return "Lo siento, no puedo responder en este momento."

    @staticmethod
    def get_openai_response(prompt: str) -> str:
        """
        Genera una respuesta utilizando OpenAI con fallback a Ollama.
        :param prompt: Mensaje del usuario.
        :return: Respuesta generada por OpenAI o Ollama (fallback).
        """
        try:
            print("LLEGO A ADAPTER")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
                top_p=1
            )
            print("RESPUESTA CHATGPT",response)
            # Verificar si la respuesta es válida
            openai_response = response['choices'][0]['message']['content'].strip()
            
            if openai_response and openai_response.lower() != 'null':
                return openai_response
            else:
                print("OpenAI devolvió una respuesta vacía o null. Intentando con Ollama...")
                return OpenAIAdapter.get_ollama_response(prompt)
        except Exception as e:
            print(f"Error inesperado con OpenAI: {e}. Intentando con Ollama...")
            return OpenAIAdapter.get_ollama_response(prompt)