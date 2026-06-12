"""
Tests completos para servicios y validaciones de HK Hotels
No requieren conexión a base de datos real
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.reserva_service import generar_codigo_unico, calcular_precio_total
from services.precio_service import PrecioService
from services.codigo_service import CodigoService
from utils.validaciones import (
    validar_email, validar_fecha, validar_fechas_rango,
    validar_telefono, sanitizar_texto
)


class TestGenerarCodigo:
    """Tests para generacion de codigos unicos"""

    def test_formato_codigo(self):
        codigo = generar_codigo_unico()
        assert codigo.startswith("HK-")
        assert len(codigo) == 8
        assert "-" in codigo

    def test_codigo_unico(self):
        codigos = [generar_codigo_unico() for _ in range(100)]
        assert len(set(codigos)) == 100


class TestCodigoService:
    """Tests para CodigoService"""

    @patch('services.codigo_service.get_db_connection')
    def test_generar_formato(self, mock_db):
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'count': 0}
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        codigo = CodigoService.generar()
        assert codigo.startswith("HK-")
        assert len(codigo) == 8


class TestCalcularPrecio:
    """Tests para calculo de precios"""

    @patch('services.reserva_service.get_db_connection')
    def test_calculo_simple(self, mock_db):
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'precio_noche': 200.0}
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        precio = calcular_precio_total(1, '2025-06-01', '2025-06-04')
        assert precio == 600.0

    @patch('services.reserva_service.get_db_connection')
    def test_calculo_con_servicios(self, mock_db):
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            {'precio_noche': 200.0},
            {'precio': 50.0},
            {'precio': 30.0},
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        precio = calcular_precio_total(1, '2025-06-01', '2025-06-03', [1, 2])
        assert precio == 480.0

    @patch('services.reserva_service.get_db_connection')
    def test_habitacion_no_encontrada(self, mock_db):
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        precio = calcular_precio_total(999, '2025-06-01', '2025-06-03')
        assert precio is None


class TestPrecioService:
    """Tests para PrecioService"""

    def test_calcular_precio_basico(self):
        resultado = PrecioService.calcular(1000, 3)
        assert resultado['subtotal'] == 3000
        assert resultado['noches'] == 3
        assert resultado['porcentaje_iva'] == 16
        assert resultado['impuestos'] == 480
        assert resultado['total'] == 3480

    def test_calcular_noches(self):
        noches = PrecioService.calcular_noches('2025-12-01', '2025-12-05')
        assert noches == 4

    def test_calcular_noches_minimo_uno(self):
        noches = PrecioService.calcular_noches('2025-12-01', '2025-12-01')
        assert noches == 1


class TestValidaciones:
    """Tests para validaciones"""

    def test_email_valido(self):
        assert validar_email('cliente@hkhotels.com') is True
        assert validar_email('correo-invalido') is False
        assert validar_email('') is False

    def test_fecha_valida(self):
        assert validar_fecha('2025-06-15') is True
        assert validar_fecha('15-06-2025') is False

    def test_fechas_rango_validas(self):
        hoy = date.today()
        checkin = (hoy + timedelta(days=5)).strftime('%Y-%m-%d')
        checkout = (hoy + timedelta(days=8)).strftime('%Y-%m-%d')
        valido, msg = validar_fechas_rango(checkin, checkout)
        assert valido is True

    def test_fechas_checkout_antes_checkin(self):
        hoy = date.today()
        checkin = (hoy + timedelta(days=8)).strftime('%Y-%m-%d')
        checkout = (hoy + timedelta(days=5)).strftime('%Y-%m-%d')
        valido, msg = validar_fechas_rango(checkin, checkout)
        assert valido is False

    def test_telefono_valido(self):
        assert validar_telefono('+34 971 123 456') is True
        assert validar_telefono('') is True

    def test_sanitizar_texto(self):
        assert sanitizar_texto('<script>alert(1)</script>') is not None
        assert sanitizar_texto('') == ''
        assert sanitizar_texto(None) == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
