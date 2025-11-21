from flask import Blueprint, request, jsonify
from contexts.chatbot_management.application.use_cases.generate_chatbot_response_use_case import GenerateChatbotResponseUseCase
from contexts.chatbot_management.application.dtos.chatbot_request import ChatbotRequestDTO
from contexts.chatbot_management.infrastructure.repositories.chatbot_repository import ChatbotRepository

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/respond', methods=['POST'])
def respond():
    try:
        """
        Endpoint para recibir un mensaje del usuario y generar una respuesta del chatbot.
        """
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        if 'user_id' not in data:
            return jsonify({"error": "No user_id provided"}), 400

        request_dto = ChatbotRequestDTO(data['message'],data['user_id'])  # Crear DTO con la entrada
        response_dto = GenerateChatbotResponseUseCase.execute(request_dto)  # Ejecutar caso de uso
        return jsonify(response_dto.to_dict())  # Convertir la respuesta a JSON
    except Exception as e:
        print(f"ERROR EN ENDPOINT: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@chatbot_bp.route('/save-voice-message', methods=['POST'])
def save_voice_message():
    """
    Guarda una transcripción de mensaje de voz en el historial.

    Request:
    {
        "user_id": "firebase_auth_uid",
        "user_message": "transcripción del usuario",
        "bot_response": "respuesta del bot",
        "audio_duration_ms": 3500,  // Opcional
        "transcription_confidence": 0.95  // Opcional (0.0-1.0)
    }
    """
    try:
        data = request.json

        user_id = data.get('user_id')
        user_message = data.get('user_message')
        bot_response = data.get('bot_response')
        audio_duration_ms = data.get('audio_duration_ms')
        transcription_confidence = data.get('transcription_confidence')

        # Validar campos requeridos
        if not user_id or not user_message or not bot_response:
            return jsonify({
                'success': False,
                'error': 'user_id, user_message y bot_response son requeridos'
            }), 400

        # Guardar en repositorio con metadatos de voz
        repository = ChatbotRepository()
        repository.save_voice_message(
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response,
            audio_duration_ms=audio_duration_ms,
            transcription_confidence=transcription_confidence
        )

        return jsonify({
            'success': True,
            'message': 'Mensaje de voz guardado exitosamente'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/history', methods=['GET'])
def get_history():
    """
    Obtiene el historial de conversaciones de un usuario.

    Query params:
    - user_id: ID del usuario (requerido)
    - limit: Número máximo de mensajes (default: 50)
    - message_type: "text" | "voice" | "all" (default: "all")
    """
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))
        message_type = request.args.get('message_type', 'all')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id es requerido'
            }), 400

        repository = ChatbotRepository()
        history = repository.get_conversation_history(
            user_id=user_id,
            limit=limit,
            message_type=message_type
        )

        return jsonify({
            'success': True,
            'messages': history
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500