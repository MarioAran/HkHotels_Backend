"""
utils/helpers.py
Funciones auxiliares generales para el backend API
"""

from datetime import datetime, date
from decimal import Decimal


def formatear_moneda(valor) -> str:
    """Formatea un número como moneda con separador de miles."""
    try:
        return f"${float(valor):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def serializar_json(obj):
    """
    Convierte tipos no serializables (date, Decimal) a tipos compatibles con JSON.
    Útil para usar con json.dumps(default=serializar_json).
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo no serializable: {type(obj)}")


def calcular_noches_estadia(fecha_checkin: str, fecha_checkout: str) -> int:
    """Calcula el número de noches entre check-in y check-out."""
    try:
        checkin = datetime.strptime(str(fecha_checkin), "%Y-%m-%d")
        checkout = datetime.strptime(str(fecha_checkout), "%Y-%m-%d")
        return max(1, (checkout - checkin).days)
    except ValueError:
        return 1


def respuesta_exitosa(data=None, message: str = "Operación exitosa"):
    """Construye una respuesta estándar de éxito para la API."""
    return {
        "success": True,
        "data": data if data is not None else {},
        "message": message
    }


def respuesta_error(message: str = "Ocurrió un error", error_code: int = 400, error: str = None):
    """Construye una respuesta estándar de error para la API."""
    respuesta = {
        "success": False,
        "message": message,
        "error_code": error_code
    }
    if error:
        respuesta["error"] = error
    return respuesta
