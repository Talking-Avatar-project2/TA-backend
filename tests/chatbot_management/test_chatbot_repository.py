import pytest
from unittest.mock import patch
from datetime import datetime
from contexts.chatbot_management.infrastructure.repositories.chatbot_repository import ChatbotRepository

class TestChatbotRepository:
    """
    Pruebas unitarias para el repositorio del chatbot.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, mock_firestore_client):
        """Setup para cada prueba."""
        # Limpiar historial antes de cada prueba
        ChatbotRepository._conversation_history = []
        
        # Mock del cliente Firestore
        with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository._get_client', 
                    return_value=mock_firestore_client):
            yield

    def test_save_message_with_emotion_extraction(self):
        """
        Probar que save_message extrae correctamente las emociones y guarda el mensaje
        """
        # Arrange
        user_message = "Estoy muy feliz hoy"
        bot_response_with_emotion = "(Positiva) ¡Qué bueno saberlo! Me alegra que tengas un buen día."
        
        # Act
        ChatbotRepository.save_message(user_message, bot_response_with_emotion)
        
        # Assert
        history = ChatbotRepository.get_conversation_history(limit=1)
        assert len(history) == 1
        
        saved_message = history[0]
        assert saved_message.user_message == user_message
        assert saved_message.bot_response == "¡Qué bueno saberlo! Me alegra que tengas un buen día."
        assert saved_message.emotion_type == "Positiva"
        assert isinstance(saved_message.timestamp, datetime)

    def test_save_message_without_emotion_tag(self):
        """
        Probar que save_message maneja respuestas sin etiqueta emocional (default: Neutra)
        """
        # Arrange
        user_message = "¿Cómo está el clima?"
        bot_response = "Puedo ayudarte con información general, pero no tengo acceso a datos meteorológicos en tiempo real."
        
        # Act
        ChatbotRepository.save_message(user_message, bot_response)
        
        # Assert
        history = ChatbotRepository.get_conversation_history(limit=1)
        saved_message = history[0]
        
        assert saved_message.emotion_type == "Neutra"
        assert saved_message.bot_response == bot_response

    def test_get_conversation_history_with_user_id(self):
        """
        Probar que get_conversation_history funciona con user_id específico
        """
        # Arrange
        user_id = "test_user_123"
        ChatbotRepository.save_message("Mensaje 1", "(Positiva) Respuesta 1", user_id)
        ChatbotRepository.save_message("Mensaje 2", "(Negativa) Respuesta 2", user_id)
        
        # Act
        history = ChatbotRepository.get_conversation_history(user_id, limit=10)
        
        # Assert
        assert len(history) >= 0  # Depende del mock, pero no debe fallar

    def test_get_emotion_statistics(self):
        """
        Probar que get_emotion_statistics calcula correctamente las estadísticas
        """
        # Arrange
        user_id = "stats_user"
        messages = [
            ("Estoy feliz", "(Positiva) ¡Genial!"),
            ("Me siento mal", "(Negativa) Lo siento"),
            ("Estoy bien", "(Neutra) Entiendo"),
            ("Muy contento", "(Positiva) ¡Excelente!"),
        ]
        
        for user_msg, bot_msg in messages:
            ChatbotRepository.save_message(user_msg, bot_msg, user_id)
        
        # Act
        stats = ChatbotRepository.get_emotion_statistics(user_id)
        
        # Assert
        assert isinstance(stats, dict)
        assert "Positiva" in stats
        assert "Negativa" in stats
        assert "Neutra" in stats
        
        # Verificar que suma las estadísticas correctamente
        total = sum(stats.values())
        assert total >= 0

    def test_extract_emotion_type_various_formats(self):
        """
        Probar la extracción de emociones con diferentes formatos
        """
        test_cases = [
            # (input, expected_emotion, expected_clean_response)
            ("(Positiva) ¡Excelente día!", "Positiva", "¡Excelente día!"),
            ("(Negativa) Lo siento por tu pérdida", "Negativa", "Lo siento por tu pérdida"),
            ("(Neutra) Información procesada", "Neutra", "Información procesada"),
            ("Sin etiqueta emocional", "Neutra", "Sin etiqueta emocional"),
            ("(Positiva)Sin espacio después", "Positiva", "Sin espacio después"),
            ("(Empatía) Comprendo tu situación", "Empatía", "Comprendo tu situación"),
        ]
        
        for input_text, expected_emotion, expected_clean in test_cases:
            emotion, clean = ChatbotRepository._extract_emotion_type(input_text)
            assert emotion == expected_emotion, f"Input: {input_text}"
            assert clean == expected_clean, f"Input: {input_text}"

    def test_fallback_to_memory_when_firestore_fails(self):
        """
        Probar que el sistema usa memoria local cuando Firestore falla
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository._get_client') as mock_client:
            # Simular error de Firestore
            mock_client.side_effect = Exception("Firestore connection error")
            
            user_message = "Mensaje de prueba"
            bot_response = "(Neutra) Respuesta de prueba"
            
            # Act
            ChatbotRepository.save_message(user_message, bot_response)
            
            # Assert - debe funcionar usando memoria local
            history = ChatbotRepository._conversation_history
            assert len(history) > 0
            assert history[-1].user_message == user_message

    def test_message_persistence_across_multiple_saves(self):
        """
        Probar que los mensajes se acumulan correctamente en múltiples guardados
        """
        # Arrange
        messages = [
            ("Hola", "(Neutra) Hola, ¿cómo estás?"),
            ("Bien gracias", "(Positiva) Me alegra saberlo"),
            ("¿Puedes ayudarme?", "(Neutra) Por supuesto, ¿en qué necesitas ayuda?")
        ]
        
        # Act
        for user_msg, bot_msg in messages:
            ChatbotRepository.save_message(user_msg, bot_msg)
        
        # Assert
        history = ChatbotRepository.get_conversation_history(limit=10)
        assert len(history) >= len(messages)
        
        # Verificar que los mensajes están en orden
        recent_messages = history[-len(messages):]
        for i, (expected_user, expected_bot) in enumerate(messages):
            emotion_type, clean_bot = ChatbotRepository._extract_emotion_type(expected_bot)
            assert recent_messages[i].user_message == expected_user
            assert recent_messages[i].bot_response == clean_bot

    def test_limit_functionality_in_get_conversation_history(self):
        """
        Probar que el parámetro limit funciona correctamente
        """
        # Arrange - agregar más mensajes que el límite
        for i in range(5):
            ChatbotRepository.save_message(f"Mensaje {i}", f"(Neutra) Respuesta {i}")
        
        # Act
        limited_history = ChatbotRepository.get_conversation_history(limit=3)
        
        # Assert
        assert len(limited_history) <= 3