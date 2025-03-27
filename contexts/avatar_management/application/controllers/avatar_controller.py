from flask import Blueprint, request, jsonify
from contexts.avatar_management.application.use_cases.animate_avatar_use_case import AnimateAvatarUseCase
from contexts.avatar_management.application.dtos.avatar_request import AvatarRequestDTO
from contexts.avatar_management.application.dtos.avatar_response import AvatarResponseDTO

avatar_bp = Blueprint('avatar', __name__)

@avatar_bp.route('/express', methods=['POST'])
def express():
    """
    Recibe la emoción del usuario y delega la animación del avatar.
    """
    data = request.get_json()
    if not data or 'emotion' not in data:
        return jsonify({"error": "Missing emotion in request"}), 400

    request_dto = AvatarRequestDTO(data['emotion'])
    response_message = AnimateAvatarUseCase.execute(request_dto)
    response_dto = AvatarResponseDTO(response_message)

    return jsonify(response_dto.to_dict()), 200