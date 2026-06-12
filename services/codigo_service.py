"""
services/codigo_service.py
Servicio para generar códigos únicos de reserva
"""
import random
import string
from datetime import datetime
from config.database import get_db_connection


class CodigoService:
    """
    Genera códigos únicos para identificar reservas.
    Formato: HK-XXXXX (prefijo + 5 caracteres alfanuméricos)
    """

    PREFIJO = "HK-"
    LONGITUD = 5

    @classmethod
    def generar(cls) -> str:
        """
        Genera un código único verificando que no exista en la BD.

        Returns:
            Código único en formato HK-XXXXX
        """
        max_intentos = 10
        for _ in range(max_intentos):
            sufijo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=cls.LONGITUD))
            codigo = f"{cls.PREFIJO}{sufijo}"

            if not cls._existe(codigo):
                return codigo

        # Fallback: usar timestamp
        timestamp = int(datetime.now().timestamp())
        return f"{cls.PREFIJO}{timestamp}"

    @classmethod
    def _existe(cls, codigo: str) -> bool:
        """Verifica si el código ya existe en la tabla de reservas."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM reservas WHERE codigo_unico = %s",
                (codigo,)
            )
            resultado = cursor.fetchone()
            cursor.close()
            return resultado['count'] > 0
        except Exception:
            return False
