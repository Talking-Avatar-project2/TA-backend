# contexts/user_management/application/controllers/user_controller.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from contexts.user_management.application.middlewares.auth_middleware import require_auth
from contexts.user_management.domain.services.user_service import UserService

user_bp = Blueprint("user_bp", __name__)

def get_user_service():
    """Inicializa el UserService de forma lazy (solo cuando se necesita)"""
    return UserService()


@user_bp.post("/create-profile")
@require_auth
def create_profile():
    """
    Crea un perfil de usuario en Firestore (CP020)

    Se llama después de que el usuario se registra en Firebase Auth

    Request (JSON):
        {
            "full_name": "Juan Pérez",
            "birth_date": "1990-01-15",  # formato: YYYY-MM-DD
            "photo_url": "https://..." (opcional)
        }

    Headers:
        Authorization: Bearer <firebase_jwt_token>

    Response:
        {
            "success": true,
            "user": {
                "user_id": "firebase_uid",
                "email": "user@example.com",
                "full_name": "Juan Pérez",
                "birth_date": "1990-01-15",
                "photo_url": "https://...",
                "created_at": "2025-01-21T..."
            }
        }
    """
    try:
        data = request.get_json(silent=True) or {}

        # Obtener datos del request
        full_name = data.get('full_name')
        birth_date_str = data.get('birth_date')
        photo_url = data.get('photo_url')

        # Validaciones
        if not full_name:
            return jsonify({'success': False, 'error': 'full_name es requerido'}), 400

        if not birth_date_str:
            return jsonify({'success': False, 'error': 'birth_date es requerido'}), 400

        # Parsear fecha de nacimiento
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'birth_date debe estar en formato YYYY-MM-DD'
            }), 400

        # Crear perfil (user_id y email vienen del token JWT)
        user_service = get_user_service()
        user = user_service.create_user_profile(
            user_id=request.user_id,
            email=request.user_email,
            full_name=full_name,
            birth_date=birth_date,
            photo_url=photo_url
        )

        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'full_name': user.full_name,
                'birth_date': user.birth_date.strftime('%Y-%m-%d'),
                'photo_url': user.photo_url,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 201

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.exception("Error al crear perfil")
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.get("/profile")
@require_auth
def get_profile():
    """
    Obtiene el perfil del usuario autenticado

    Headers:
        Authorization: Bearer <firebase_jwt_token>

    Response:
        {
            "success": true,
            "user": {
                "user_id": "...",
                "email": "...",
                "full_name": "...",
                "birth_date": "1990-01-15",
                "photo_url": "..."
            }
        }
    """
    try:
        user_service = get_user_service()
        user = user_service.get_user_profile(request.user_id)

        if not user:
            return jsonify({
                'success': False,
                'error': 'Perfil no encontrado'
            }), 404

        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'full_name': user.full_name,
                'birth_date': user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
                'photo_url': user.photo_url,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        }), 200

    except Exception as e:
        current_app.logger.exception("Error al obtener perfil")
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.put("/profile")
@require_auth
def update_profile():
    """
    Actualiza el perfil del usuario (CP023)

    Request (JSON):
        {
            "full_name": "Nuevo Nombre" (opcional),
            "birth_date": "1990-01-15" (opcional),
            "photo_url": "https://..." (opcional)
        }

    Headers:
        Authorization: Bearer <firebase_jwt_token>

    Response:
        {
            "success": true,
            "user": {...}
        }
    """
    try:
        data = request.get_json(silent=True) or {}

        full_name = data.get('full_name')
        birth_date_str = data.get('birth_date')
        photo_url = data.get('photo_url')

        # Parsear fecha si viene
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'birth_date debe estar en formato YYYY-MM-DD'
                }), 400

        # Actualizar perfil
        user_service = get_user_service()
        user = user_service.update_user_profile(
            user_id=request.user_id,
            full_name=full_name,
            birth_date=birth_date,
            photo_url=photo_url
        )

        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'full_name': user.full_name,
                'birth_date': user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
                'photo_url': user.photo_url,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            },
            'message': 'Perfil actualizado exitosamente'
        }), 200

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.exception("Error al actualizar perfil")
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.post("/verify-token")
@require_auth
def verify_token():
    """
    Verifica que un token JWT sea válido (CP015/CP016)

    Este endpoint se puede usar para validar sesión

    Headers:
        Authorization: Bearer <firebase_jwt_token>

    Response:
        {
            "success": true,
            "user_id": "...",
            "email": "...",
            "message": "Token válido"
        }
    """
    return jsonify({
        'success': True,
        'user_id': request.user_id,
        'email': request.user_email,
        'message': 'Token válido'
    }), 200


@user_bp.post("/logout")
@require_auth
def logout():
    """
    Cierre de sesión (CP017)

    En Firebase Auth, el logout se maneja en el cliente
    Este endpoint es opcional y puede usarse para limpiar datos del servidor

    Headers:
        Authorization: Bearer <firebase_jwt_token>

    Response:
        {
            "success": true,
            "message": "Sesión cerrada exitosamente"
        }
    """
    # Aquí podrías agregar lógica adicional como:
    # - Limpiar sesiones del servidor
    # - Registrar el logout en logs
    # - Notificar a otros servicios

    current_app.logger.info(f"Usuario {request.user_id} cerró sesión")

    return jsonify({
        'success': True,
        'message': 'Sesión cerrada exitosamente'
    }), 200


@user_bp.get("/health")
def health():
    """Health check del módulo de usuarios"""
    return jsonify({
        'success': True,
        'module': 'user_management',
        'status': 'active'
    }), 200
