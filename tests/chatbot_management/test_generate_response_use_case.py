import pytest
import time
from unittest.mock import patch
from contexts.chatbot_management.application.use_cases.generate_chatbot_response_use_case import GenerateChatbotResponseUseCase
from contexts.chatbot_management.application.dtos.chatbot_request import ChatbotRequestDTO
from contexts.chatbot_management.application.dtos.chatbot_response import ChatbotResponseDTO

class TestGenerateChatbotResponseUseCase:
    """
    Pruebas unitarias para el caso de uso de generación de respuesta del chatbot.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, mock_firestore_client):
        """Setup para cada prueba."""
        with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository._get_client', 
                    return_value=mock_firestore_client):
            yield

    def test_execute_with_positive_emotion(self):
        """
        Probar que execute() procesa correctamente emociones positivas
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            mock_ollama.return_value = "(Positiva) ¡Excelente! Me alegra saber que estás feliz."
            
            request_dto = ChatbotRequestDTO("Estoy muy feliz hoy")
            
            # Act
            response_dto = GenerateChatbotResponseUseCase.execute(request_dto)
            
            # Assert
            assert isinstance(response_dto, ChatbotResponseDTO)
            assert response_dto.response == "¡Excelente! Me alegra saber que estás feliz."
            
            # Verificar que se llamó a Ollama
            mock_ollama.assert_called_once()

    def test_execute_with_negative_emotion(self):
        """
        Probar que execute() procesa correctamente emociones negativas
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            mock_ollama.return_value = "(Negativa) Siento que estés pasando por un momento difícil. ¿Quieres hablar sobre ello?"
            
            request_dto = ChatbotRequestDTO("Me siento muy triste")
            
            # Act
            response_dto = GenerateChatbotResponseUseCase.execute(request_dto)
            
            # Assert
            assert isinstance(response_dto, ChatbotResponseDTO)
            assert "Siento que estés pasando por un momento difícil" in response_dto.response
            assert "¿Quieres hablar sobre ello?" in response_dto.response

    def test_execute_with_neutral_ambiguous_message(self):
        """
        Probar que execute() maneja mensajes ambiguos/neutrales
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            mock_ollama.return_value = "(Neutra) ¿Podrías contarme más sobre cómo te sientes hoy?"
            
            request_dto = ChatbotRequestDTO("Hoy es un día muy soleado, me pregunto si lloverá")
            
            # Act
            response_dto = GenerateChatbotResponseUseCase.execute(request_dto)
            
            # Assert
            assert isinstance(response_dto, ChatbotResponseDTO)
            assert "¿Podrías contarme más" in response_dto.response

    def test_execute_with_mixed_emotions(self):
        """
        Probar que execute() maneja emociones mezcladas
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            mock_ollama.return_value = "(Neutra) Veo que tienes sentimientos encontrados. ¿Cuál sientes que predomina más?"
            
            request_dto = ChatbotRequestDTO("Me siento feliz pero también ansioso")
            
            # Act
            response_dto = GenerateChatbotResponseUseCase.execute(request_dto)
            
            # Assert
            assert isinstance(response_dto, ChatbotResponseDTO)
            assert "sentimientos encontrados" in response_dto.response.lower()

    def test_execute_respects_conversation_history(self):
        """
        Probar que execute() pasa el historial de conversación a Ollama
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository.get_conversation_history') as mock_history:
                
                # Configurar mock del historial
                mock_history.return_value = []  # Historial vacío para simplicidad
                mock_ollama.return_value = "(Neutra) Respuesta de prueba"
                
                request_dto = ChatbotRequestDTO("Mensaje de prueba")
                
                # Act
                GenerateChatbotResponseUseCase.execute(request_dto)
                
                # Assert
                mock_history.assert_called_once_with(user_id="default_user", limit=10)
                mock_ollama.assert_called_once()
                
                # Verificar que se pasó el historial a Ollama
                call_args = mock_ollama.call_args
                assert call_args[0][0] == "Mensaje de prueba"  # Mensaje del usuario
                assert call_args[0][1] == []  # Historial (vacío en este caso)

    def test_execute_performance_requirement(self):
        """
        CS-03: Probar que execute() cumple el requisito de tiempo < 3 segundos
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            # Simular una respuesta rápida
            mock_ollama.return_value = "(Neutra) Respuesta rápida"
            
            request_dto = ChatbotRequestDTO("Mensaje de prueba de rendimiento")
            
            # Act
            start_time = time.time()
            response_dto = GenerateChatbotResponseUseCase.execute(request_dto)
            end_time = time.time()
            
            # Assert
            response_time = end_time - start_time
            assert response_time < 3.0, f"Tiempo de respuesta {response_time:.2f}s excede los 3 segundos requeridos"
            assert isinstance(response_dto, ChatbotResponseDTO)

    def test_execute_saves_message_to_repository(self):
        """
        Probar que execute() guarda el mensaje en el repositorio
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository.save_message') as mock_save:
                
                mock_ollama.return_value = "(Positiva) Respuesta de prueba"
                request_dto = ChatbotRequestDTO("Mensaje de prueba")
                
                # Act
                GenerateChatbotResponseUseCase.execute(request_dto)
                
                # Assert
                mock_save.assert_called_once_with(
                    user_message="Mensaje de prueba",
                    bot_response="(Positiva) Respuesta de prueba",
                    user_id="default_user"
                )

    def test_execute_with_user_id_parameter(self):
        """
        Probar que execute() maneja correctamente el parámetro user_id
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository.save_message') as mock_save:
                with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository.get_conversation_history') as mock_history:
                    
                    mock_ollama.return_value = "(Neutra) Respuesta personalizada"
                    mock_history.return_value = []
                    
                    request_dto = ChatbotRequestDTO("Mensaje personalizado")
                    user_id = "user123"
                    
                    # Act
                    GenerateChatbotResponseUseCase.execute(request_dto, user_id)
                    
                    # Assert
                    mock_history.assert_called_once_with(user_id=user_id, limit=10)
                    mock_save.assert_called_once_with(
                        user_message="Mensaje personalizado",
                        bot_response="(Neutra) Respuesta personalizada",
                        user_id=user_id
                    )

    def test_execute_handles_exceptions_gracefully(self):
        """
        Probar que execute() maneja excepciones correctamente
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            # Simular error en Ollama
            mock_ollama.side_effect = Exception("Error de conexión con Ollama")
            
            request_dto = ChatbotRequestDTO("Mensaje que causará error")
            
            # Act & Assert
            with pytest.raises(Exception):
                GenerateChatbotResponseUseCase.execute(request_dto)

    def test_get_user_statistics(self):
        """
        Probar que get_user_statistics() funciona correctamente
        """
        # Arrange
        user_id = "test_stats_user"
        expected_stats = {"Positiva": 5, "Negativa": 3, "Neutra": 2}
        
        with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository.get_emotion_statistics') as mock_stats:
            mock_stats.return_value = expected_stats
            
            # Act
            result = GenerateChatbotResponseUseCase.get_user_statistics(user_id)
            
            # Assert
            assert result == expected_stats
            mock_stats.assert_called_once_with(user_id)

    def test_get_user_history(self):
        """
        Probar que get_user_history() funciona correctamente
        """
        # Arrange
        user_id = "test_history_user"
        limit = 5
        expected_history = []  # Lista vacía para simplicidad
        
        with patch('contexts.chatbot_management.infrastructure.repositories.chatbot_repository.ChatbotRepository.get_conversation_history') as mock_history:
            mock_history.return_value = expected_history
            
            # Act
            result = GenerateChatbotResponseUseCase.get_user_history(user_id, limit)
            
            # Assert
            assert result == expected_history
            mock_history.assert_called_once_with(user_id, limit)

    def test_integration_emotion_flow_complete(self):
        """
        Prueba de integración que verifica todo el flujo de detección emocional
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            mock_ollama.return_value = "(Negativa) Entiendo que te sientes triste. ¿Quieres contarme qué está pasando?"
            
            request_dto = ChatbotRequestDTO("Estoy muy triste, todo está saliendo mal")
            
            # Act
            start_time = time.time()
            response_dto = GenerateChatbotResponseUseCase.execute(request_dto)
            end_time = time.time()
            
            # Assert - Verificar todos los aspectos del flujo
            # 1. Tiempo de respuesta
            assert (end_time - start_time) < 3.0
            
            # 2. Respuesta empática apropiada
            response_text = response_dto.response.lower()
            assert any(word in response_text for word in ["entiendo", "siento", "comprendo"])
            
            # 3. Solicita más información (comportamiento esperado)
            assert "?" in response_dto.response
            
            # 4. Respuesta no vacía
            assert len(response_dto.response.strip()) > 0

    def test_message_flow_preserves_conversation_context(self):
        """
        Probar que el flujo de mensajes preserva el contexto de la conversación
        """
        # Arrange
        with patch('contexts.chatbot_management.infrastructure.adapters.openai_adapter.OpenAIAdapter.get_ollama_response') as mock_ollama:
            # Simular una conversación secuencial
            mock_responses = [
                "(Negativa) Lo siento, ¿qué está pasando?",
                "(Positiva) ¡Me alegra saber que mejoraste!"
            ]
            
            mock_ollama.side_effect = mock_responses
            
            # Primer mensaje
            request1 = ChatbotRequestDTO("Me siento mal")
            response1 = GenerateChatbotResponseUseCase.execute(request1)
            
            # Segundo mensaje
            request2 = ChatbotRequestDTO("Ya me siento mejor, gracias")
            response2 = GenerateChatbotResponseUseCase.execute(request2)
            
            # Assert
            assert "siento" in response1.response.lower()
            assert "alegra" in response2.response.lower()
            
            # Verificar que se llamó a Ollama dos veces
            assert mock_ollama.call_count == 2