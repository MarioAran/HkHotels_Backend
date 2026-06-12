"""
services/precio_service.py
Servicio de cálculo de precios con impuestos
"""
from datetime import datetime


class PrecioService:
    """
    Servicio para calcular precios de reservas.
    Aplica IVA y retorna desglose completo.
    """

    IVA_PORCENTAJE = 16  # 16% IVA por defecto

    @classmethod
    def calcular(cls, precio_noche: float, noches: int) -> dict:
        """
        Calcula el desglose completo de precios para una reserva.

        Args:
            precio_noche: Precio por noche de la habitación
            noches: Número de noches de la estadía

        Returns:
            dict con subtotal, impuestos, total y desglose
        """
        precio_noche = float(precio_noche)
        noches = int(noches)
        iva_decimal = cls.IVA_PORCENTAJE / 100

        subtotal = round(precio_noche * noches, 2)
        impuestos = round(subtotal * iva_decimal, 2)
        total = round(subtotal + impuestos, 2)

        return {
            "precio_noche": precio_noche,
            "noches": noches,
            "subtotal": subtotal,
            "porcentaje_iva": cls.IVA_PORCENTAJE,
            "impuestos": impuestos,
            "total": total
        }

    @classmethod
    def calcular_noches(cls, fecha_checkin: str, fecha_checkout: str) -> int:
        """
        Calcula el número de noches entre dos fechas.

        Args:
            fecha_checkin: Fecha de entrada en formato YYYY-MM-DD
            fecha_checkout: Fecha de salida en formato YYYY-MM-DD

        Returns:
            Número de noches (mínimo 1)
        """
        try:
            checkin = datetime.strptime(str(fecha_checkin), "%Y-%m-%d")
            checkout = datetime.strptime(str(fecha_checkout), "%Y-%m-%d")
            delta = (checkout - checkin).days
            return max(1, delta)
        except ValueError:
            return 1
