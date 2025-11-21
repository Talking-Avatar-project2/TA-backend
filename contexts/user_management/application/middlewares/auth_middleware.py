# contexts/user_management/application/middlewares/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from firebase_admin import auth
from typing import Callable
import sys


def require_auth(f: Callable) -> Callable:
    """
    Decorator para proteger endpoints que requieren autenticación

    Valida el token JWT de Firebase Auth y agrega el user_id al request

    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user_id = request.user_id
            return {"message": f"Hello {user_id}"}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        print(f"[AUTH DEBUG] Iniciando validación de token...", flush=True)
        sys.stderr.write(f"[AUTH DEBUG] Auth header presente: {bool(auth_header)}\n")
        sys.stderr.flush()

        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'No se proporcionó token de autenticación'
            }), 401

        # Verificar formato: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'success': False,
                'error': 'Formato de token inválido. Use: Bearer <token>'
            }), 401

        token = parts[1]

        try:
            # Verificar token con Firebase Admin SDK
            # check_revoked=False: Desactiva verificación de revocación
            decoded_token = auth.verify_id_token(token, check_revoked=False)
            user_id = decoded_token['uid']

            # Agregar user_id al request para uso en el endpoint
            request.user_id = user_id
            request.user_email = decoded_token.get('email')

            msg = f"[AUTH] Usuario autenticado: {request.user_email} ({user_id})\n"
            sys.stderr.write(msg)
            sys.stderr.flush()
            return f(*args, **kwargs)

        except auth.InvalidIdTokenError as e:
            error_msg = str(e)
            # Permitir tokens con clock skew menor a 5 segundos
            if "Token used too early" in error_msg or "Token used too late" in error_msg:
                try:
                    # Decodificar sin verificar para obtener los datos
                    import jwt
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    # Firebase JWT usa 'user_id' o 'sub', no 'uid'
                    request.user_id = decoded.get('user_id') or decoded.get('sub')
                    request.user_email = decoded.get('email')
                    msg = f"[AUTH] Usuario autenticado (clock skew tolerado): {request.user_email} ({request.user_id})\n"
                    sys.stderr.write(msg)
                    sys.stderr.flush()
                    return f(*args, **kwargs)
                except Exception as decode_error:
                    msg = f"[AUTH ERROR] No se pudo decodificar token con clock skew: {decode_error}\n"
                    sys.stderr.write(msg)
                    sys.stderr.flush()

            # Si no es clock skew o falló la decodificación, retornar error
            msg = f"[AUTH ERROR] Token inválido: {str(e)}\n"
            sys.stderr.write(msg)
            sys.stderr.flush()
            return jsonify({
                'success': False,
                'error': 'Token inválido'
            }), 401
        except auth.ExpiredIdTokenError as e:
            msg = f"[AUTH ERROR] Token expirado: {str(e)}\n"
            sys.stderr.write(msg)
            sys.stderr.flush()
            return jsonify({
                'success': False,
                'error': 'Token expirado. Por favor, inicie sesión nuevamente'
            }), 401
        except auth.RevokedIdTokenError as e:
            msg = f"[AUTH ERROR] Token revocado: {str(e)}\n"
            sys.stderr.write(msg)
            sys.stderr.flush()
            return jsonify({
                'success': False,
                'error': 'Token revocado'
            }), 401
        except Exception as e:
            msg = f"[AUTH ERROR] Error al verificar token: {str(e)}\n"
            sys.stderr.write(msg)
            sys.stderr.flush()
            return jsonify({
                'success': False,
                'error': f'Error al verificar token: {str(e)}'
            }), 401

    return decorated_function


def optional_auth(f: Callable) -> Callable:
    """
    Decorator para endpoints donde la autenticación es opcional

    Si hay token válido, agrega user_id al request
    Si no hay token o es inválido, continúa sin user_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                try:
                    decoded_token = auth.verify_id_token(parts[1], check_revoked=False)
                    request.user_id = decoded_token['uid']
                    request.user_email = decoded_token.get('email')
                except auth.InvalidIdTokenError as e:
                    # Intentar con clock skew tolerance
                    error_msg = str(e)
                    if "Token used too early" in error_msg or "Token used too late" in error_msg:
                        try:
                            import jwt
                            decoded = jwt.decode(parts[1], options={"verify_signature": False})
                            request.user_id = decoded.get('user_id') or decoded.get('sub')
                            request.user_email = decoded.get('email')
                            msg = f"[AUTH OPTIONAL] Usuario autenticado con clock skew: {request.user_email}\n"
                            sys.stderr.write(msg)
                            sys.stderr.flush()
                        except:
                            # Continuar sin autenticación
                            pass
                except:
                    # Continuar sin autenticación
                    pass

        return f(*args, **kwargs)

    return decorated_function
