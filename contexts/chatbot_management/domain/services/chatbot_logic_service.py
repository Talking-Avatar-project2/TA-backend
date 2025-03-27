from contexts.chatbot_management.infrastructure.adapters.openai_adapter import OpenAIAdapter
from contexts.chatbot_management.infrastructure.processors.text_preprocessing import TextPreprocessing

class ChatbotLogicService:
    """
    Servicio que maneja la lógica del chatbot antes de enviar los mensajes a OpenAI.
    """

    @staticmethod
    def process_user_message(user_message: str) -> str:
        """
        Procesa el mensaje del usuario antes de enviarlo a OpenAI.
        :param user_message: Entrada del usuario.
        :return: Respuesta procesada por la IA.
        """
        # 1️⃣ Preprocesamiento del texto
        cleaned_message = TextPreprocessing.clean_text(user_message)

        # 2️⃣ Verificación de mensajes vacíos o irrelevantes
        if not cleaned_message or len(cleaned_message) < 2:
            return "No entiendo tu mensaje. ¿Podrías reformularlo?"

        # 3️⃣ Lógica de respuestas automáticas sin OpenAI
        if "ayuda" in cleaned_message:
            return "Soy un asistente emocional. Puedes contarme cómo te sientes o preguntar sobre bienestar emocional."

        # 4️⃣ Enviar mensaje procesado a OpenAI
        return OpenAIAdapter.get_openai_response(cleaned_message)
