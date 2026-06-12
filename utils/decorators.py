"""
utils/decorators.py
Decoradores reutilizables para los endpoints de la API
"""
import logging
from functools import wraps
from flask import jsonify, request

logger = logging.getLogger(__name__)


def manejar_errores_api(f):
    """
    Decorador que envuelve endpoints de API en un try/except genérico,
    garantizando respuestas JSON consistentes incluso ante errores no previstos.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error no controlado en {f.__name__}: {e}")
            return jsonify({
                "success": False,
                "message": "Ocurrió un error interno en el servidor.",
                "error_code": 500
            }), 500
    return decorated_function


def validar_json_body(f):
    """
    Decorador que valida que el body de la petición sea JSON válido
    antes de ejecutar la función de la ruta.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "El cuerpo de la petición debe ser JSON.",
                "error_code": 400
            }), 400
        return f(*args, **kwargs)
    return decorated_function
