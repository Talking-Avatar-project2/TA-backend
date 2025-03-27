import openai
import os

class OpenAIAdapter:
    """
    Adaptador para interactuar con OpenAI API.
    """

    openai.api_key = os.getenv("OPENAI_API_KEY")  # Se obtiene desde variables de entorno

    @staticmethod
    def get_openai_response(prompt: str) -> str:
        """
        Genera una respuesta utilizando OpenAI.
        :param prompt: Mensaje del usuario.
        :return: Respuesta generada por OpenAI.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
                top_p=1
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error con la API de OpenAI: {e}")
            return "Lo siento, no puedo responder en este momento."
