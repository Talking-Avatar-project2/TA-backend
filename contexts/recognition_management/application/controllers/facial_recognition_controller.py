from flask import Blueprint, jsonify, request
from contexts.recognition_management.application.use_cases.facial_recognition_use_case import FacialRecognitionUseCase
from contexts.recognition_management.application.dtos.facial_recognition_request import FacialRecognitionRequest
from contexts.recognition_management.application.dtos.facial_recognition_response import FacialRecognitionResponse

facial_recognition_bp = Blueprint('facial_recognition', __name__)

@facial_recognition_bp.route('/process-avatar-images', methods=['GET'])
def process_avatar_images():
    result = FacialRecognitionUseCase.analyze_images_for_avatar()
    return jsonify({"message": result})

@facial_recognition_bp.route('/stream', methods=['GET'])
def stream():
    result = FacialRecognitionUseCase.process_stream()
    return jsonify({"message": result})

@facial_recognition_bp.route('/recognize', methods=['POST'])
def recognize():
    try:
        request_data = FacialRecognitionRequest(**request.get_json())
        result = FacialRecognitionUseCase.process_face_data(request_data.image_data)
        response = FacialRecognitionResponse(result)
        return jsonify(response.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
