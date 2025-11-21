from typing import Any, Dict, List
from contexts.chatbot_management.domain.repositories.chatbot_repository_interface import ChatbotRepositoryInterface
from contexts.chatbot_management.domain.entities.chatbot_message import ChatbotMessage
from shared.infrastructure.firestore_client import FirestoreClient
import re

class ChatbotRepository(ChatbotRepositoryInterface):
    """Implementación en memoria del repositorio del chatbot."""

    _firestore_client = None
    _conversation_history = []  # Simulación de almacenamiento en memoria

    @classmethod
    def _get_client(cls):
        if cls._firestore_client is None:
            cls._firestore_client = FirestoreClient()
        return cls._firestore_client

    @staticmethod
    def _extract_emotion_type(bot_response: str) -> tuple:
        """
        Extrae el tipo de emoción de la respuesta del bot.
        :param bot_response: Respuesta completa del bot.
        :return: Tupla (emotion_type, clean_response)
        """
        # Buscar patrones como (Positiva), (Negativa), (Neutra)
        match = re.match(r'\(([^)]+)\)\s*(.*)', bot_response, re.DOTALL)
        
        if match:
            emotion_type = match.group(1).strip()
            clean_response = match.group(2).strip()
            return emotion_type, clean_response
        
        # Si no se encuentra patrón, asumir Neutra
        return "Neutra", bot_response
    @staticmethod
    def save_message(user_message: str, bot_response: str, user_id: str):
        """
        Guarda el mensaje en Firestore y en el cache local.
        :param user_message: Mensaje del usuario.
        :param bot_response: Respuesta del bot (puede incluir etiqueta de emoción).
        :param user_id: ID del usuario para organizar conversaciones.
        """
        try:
            # Extraer tipo de emoción de la respuesta
            emotion_type, clean_response = ChatbotRepository._extract_emotion_type(bot_response)

            # Crear mensaje
            message = ChatbotMessage(user_message, clean_response, emotion_type)

            # Guardar en Firestore
            client = ChatbotRepository._get_client()

            doc_data = {
                'user_message': user_message,
                'bot_response': clean_response,
                'emotion_type': emotion_type,
                'timestamp': message.timestamp
            }

            doc_id = client.add_document(f'users/{user_id}/conversations', doc_data)
            message.message_id = doc_id
            # Actualizar cache local
            ChatbotRepository._conversation_history.append(message)
            
            print(f"[OK] Mensaje guardado en Firestore: {emotion_type}")

        except Exception as e:
            print(f"❌ Error guardando mensaje en Firestore: {e}")
            # Fallback a memoria local
            emotion_type, clean_response = ChatbotRepository._extract_emotion_type(bot_response)
            message = ChatbotMessage(user_message, clean_response, emotion_type)
            ChatbotRepository._conversation_history.append(message)

    @staticmethod
    def get_conversation_history(user_id: str, limit: int = 50, message_type: str = 'all')-> List[Dict[str, Any]]:
        """
        Obtiene los últimos mensajes de la conversación desde Firestore.
        :param user_id: ID del usuario.
        :param limit: Número máximo de mensajes a obtener.
        :param message_type: Tipo de mensaje a filtrar ("text", "voice", "all").
        :return: Lista de ChatbotMessage.
        """
        try:
            client = ChatbotRepository._get_client()
            
            # Obtener mensajes ordenados por timestamp
            docs = client.get_documents(
                f'users/{user_id}/conversations', 
                order_by='timestamp', 
                limit=limit
            )
            
            messages = []
            for doc in docs:
                # Filtrar por tipo de mensaje si se especificó
                doc_message_type = doc.get('message_type', 'text')  # Default es 'text' para mensajes antiguos
                if message_type != 'all' and doc_message_type != message_type:
                    continue

                message_dict = {
                    'user_message': doc['user_message'],
                    'bot_response': doc['bot_response'],
                    'emotion_type': doc['emotion_type'],
                    'timestamp': doc['timestamp'],
                    'message_id': doc['_id'],
                    'message_type': doc_message_type
                }
                messages.append(message_dict)

            # Invertir para tener orden cronológico
            messages.reverse()

            return messages
            
        except Exception as e:
            print(f"❌ Error obteniendo historial de Firestore: {e}")
            # Fallback a cache local
            return ChatbotRepository._conversation_history[-limit:]

    @staticmethod
    def get_emotion_statistics(user_id: str = "default_user"):
        """
        Obtiene estadísticas de emociones del usuario.
        :param user_id: ID del usuario.
        :return: Diccionario con conteo de emociones.
        """
        try:
            client = ChatbotRepository._get_client()
            
            docs = client.get_documents(f'users/{user_id}/conversations')
            
            stats = {"Positiva": 0, "Negativa": 0, "Neutra": 0}
            
            for doc in docs:
                emotion = doc.get('emotion_type', 'Neutra')
                if emotion in stats:
                    stats[emotion] += 1
            
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {"Positiva": 0, "Negativa": 0, "Neutra": 0}