# contexts/profile_management/application/controllers/profile_controller.py
from flask import Blueprint, request, jsonify, current_app
from contexts.profile_management.domain.services.firebase_storage_service import FirebaseStorageService
from contexts.user_management.application.middlewares.auth_middleware import optional_auth
from contexts.user_management.domain.services.user_service import UserService

profile_bp = Blueprint("profile_bp", __name__)

def get_user_service():
    """Inicializa el UserService de forma lazy (solo cuando se necesita)"""
    return UserService()


@profile_bp.post("/upload-photo")
@optional_auth
def upload_profile_photo():
    """
    Sube foto de perfil a Firebase Storage

    Request:
        - Multipart form-data
        - Campo 'photo': archivo de imagen
        - Campo 'user_id': ID del usuario (opcional, default: 'default_user')

    Response:
        {
            "success": true,
            "photo_url": "https://storage.googleapis.com/...",
            "message": "Foto subida exitosamente"
        }
    """
    try:
        # 1. Validar que se envió un archivo
        if 'photo' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se envió ninguna foto'
            }), 400

        file = request.files['photo']

        # 2. Validar que el archivo tiene nombre
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Archivo sin nombre'
            }), 400

        # 3. Validar extensión
        if not FirebaseStorageService.is_allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Tipo de archivo no permitido. Usa: {FirebaseStorageService.get_allowed_extensions_str()}'
            }), 400

        # 4. Validar tamaño
        is_valid_size, file_size = FirebaseStorageService.validate_file_size(file)
        if not is_valid_size:
            return jsonify({
                'success': False,
                'error': f'Archivo demasiado grande ({file_size} bytes). Máximo: {FirebaseStorageService.MAX_FILE_SIZE} bytes (5MB)'
            }), 400

        # 5. Obtener user_id
        user_id = request.form.get('user_id', 'default_user')

        # 6. Subir a Firebase Storage
        photo_url = FirebaseStorageService.upload_profile_photo(
            file=file,
            user_id=user_id,
            content_type=file.content_type or 'image/jpeg'
        )

        current_app.logger.info(f"[OK] Foto de perfil subida: {user_id} -> {photo_url}")

        # 7. Actualizar URL en perfil de Firestore (si el usuario está autenticado)
        if hasattr(request, 'user_id') and request.user_id == user_id:
            try:
                user_service = get_user_service()
                user_service.update_photo_url(user_id, photo_url)
                current_app.logger.info(f"[OK] Perfil actualizado con nueva foto: {user_id}")
            except Exception as e:
                # No fallar si hay error al actualizar Firestore, ya que la foto ya se subió
                current_app.logger.warning(f"[WARN] No se pudo actualizar perfil: {e}")

        return jsonify({
            'success': True,
            'photo_url': photo_url,
            'message': 'Foto de perfil subida exitosamente'
        }), 200

    except Exception as e:
        current_app.logger.exception("Error al subir foto de perfil")
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }), 500


@profile_bp.delete("/delete-photo")
def delete_profile_photo():
    """
    Elimina la foto de perfil de Firebase Storage

    Request:
        {
            "user_id": "default_user"
        }

    Response:
        {
            "success": true,
            "message": "Foto eliminada exitosamente"
        }
    """
    try:
        # 1. Obtener user_id
        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id', 'default_user')

        # 2. Eliminar fotos del usuario
        deleted_count = FirebaseStorageService.delete_user_photos(user_id)

        if deleted_count == 0:
            return jsonify({
                'success': True,
                'message': 'No había foto de perfil para eliminar'
            }), 200

        current_app.logger.info(f"🗑️  Fotos eliminadas: {user_id} ({deleted_count} archivo(s))")

        return jsonify({
            'success': True,
            'message': f'Foto de perfil eliminada ({deleted_count} archivo(s))'
        }), 200

    except Exception as e:
        current_app.logger.exception("Error al eliminar foto de perfil")
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }), 500


@profile_bp.get("/health")
def health_check():
    """Endpoint de salud para verificar que el módulo funciona"""
    return jsonify({
        'success': True,
        'module': 'profile_management',
        'status': 'active'
    }), 200
