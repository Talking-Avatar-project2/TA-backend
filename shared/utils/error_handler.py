# shared/utils/error_handler.py
from flask import jsonify

def handle_errors(error):
    error_message = {
        "error": str(error),
        "message": "Ocurrió un error inesperado. Contacte al administrador."
    }

    status_code = getattr(error, "code", 500)
    return jsonify(error_message), status_code
