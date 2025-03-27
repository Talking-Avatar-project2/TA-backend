from flask import Blueprint, request, jsonify
from contexts.chatbot_management.application.use_cases.generate_chatbot_response_use_case import GenerateChatbotResponseUseCase
from contexts.chatbot_management.application.dtos.chatbot_request import ChatbotRequestDTO

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/respond', methods=['POST'])
def respond():
    """
    Endpoint para recibir un mensaje del usuario y generar una respuesta del chatbot.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    request_dto = ChatbotRequestDTO(data['message'])  # Crear DTO con la entrada
    response_dto = GenerateChatbotResponseUseCase.execute(request_dto)  # Ejecutar caso de uso

    return jsonify(response_dto.to_dict())  # Convertir la respuesta a JSON
