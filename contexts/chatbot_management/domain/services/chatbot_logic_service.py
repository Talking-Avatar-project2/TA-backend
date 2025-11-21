from contexts.chatbot_management.infrastructure.adapters.openai_adapter import OpenAIAdapter
from contexts.chatbot_management.infrastructure.processors.text_preprocessing import TextPreprocessing
from contexts.chatbot_management.infrastructure.repositories.chatbot_repository import ChatbotRepository

class ChatbotLogicService:
    """
    Servicio que maneja la lógica del chatbot antes de enviar los mensajes a OpenAI.
    """

    @staticmethod
    def process_user_message(user_message: str, user_id: str) -> str:
        """
        Procesa el mensaje del usuario antes de enviarlo a OpenAI.
        :param user_message: Entrada del usuario.
        :param user_id: ID del usuario para cargar su historial.
        :return: Respuesta procesada por la IA.
        """
        # 1. Preprocesamiento del texto
        cleaned_message = TextPreprocessing.clean_text(user_message)

        # 2. Verificación de mensajes vacíos o irrelevantes
        if not cleaned_message or len(cleaned_message) < 2:
            return "No entiendo tu mensaje. ¿Podrías reformularlo?"

        # 3. Enviar mensaje procesado a OpenAI
        #return OpenAIAdapter.get_openai_response(cleaned_message)
        return OpenAIAdapter.get_ollama_response(cleaned_message, ChatbotRepository.get_conversation_history(user_id))
