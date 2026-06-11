"""
Funciones de validación para datos de entrada
"""
import re
from datetime import datetime


def validar_email(email):
    """Valida que el email tenga un formato correcto"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_fecha(fecha_str):
    """Valida que una fecha tenga formato YYYY-MM-DD"""
    try:
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validar_fechas_rango(fecha_inicio, fecha_fin):
    """
    Valida un rango de fechas:
    - Formato correcto
    - Fecha fin posterior a fecha inicio
    - No en el pasado
    """
    if not validar_fecha(fecha_inicio) or not validar_fecha(fecha_fin):
        return False, "Formato de fecha inválido. Use YYYY-MM-DD"
    
    inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if fin <= inicio:
        return False, "La fecha de salida debe ser posterior a la fecha de entrada"
    
    if inicio < hoy:
        return False, "La fecha de entrada no puede ser en el pasado"
    
    return True, None


def validar_telefono(telefono):
    """Valida formato de teléfono (acepta +, dígitos, espacios y guiones)"""
    if not telefono:
        return True  # Teléfono es opcional
    patron = r'^\+?[\d\s\-]{7,20}$'
    return re.match(patron, telefono) is not None


def sanitizar_texto(texto):
    """Elimina caracteres peligrosos del texto"""
    if not texto:
        return ""
    # Eliminar caracteres que podrían usarse para inyección
    caracteres_peligrosos = ['<', '>', '"', "'", ';', '--', '/*', '*/']
    for caracter in caracteres_peligrosos:
        texto = texto.replace(caracter, '')
    return texto.strip()