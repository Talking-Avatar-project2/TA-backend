from contexts.chatbot_management.domain.services.chatbot_logic_service import ChatbotLogicService
from contexts.chatbot_management.infrastructure.repositories.chatbot_repository import ChatbotRepository
from contexts.chatbot_management.application.dtos.chatbot_request import ChatbotRequestDTO
from contexts.chatbot_management.application.dtos.chatbot_response import ChatbotResponseDTO

class GenerateChatbotResponseUseCase:
    @staticmethod
    def execute(request_dto: ChatbotRequestDTO) -> ChatbotResponseDTO:
        """
        Genera una respuesta del chatbot aplicando lógica y almacenamiento.
        :param request_dto: Objeto DTO con el mensaje del usuario.
        :return: Respuesta generada por la IA en formato DTO.
        """
        response = ChatbotLogicService.process_user_message(request_dto.user_message)
        # Guardar conversación en el historial
        ChatbotRepository.save_message(request_dto.user_message, response)
        return ChatbotResponseDTO(response)
