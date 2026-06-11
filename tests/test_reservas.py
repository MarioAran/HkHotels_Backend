"""
Tests para el módulo de reservas
"""
import pytest
from unittest.mock import Mock, patch
from services.reserva_service import generar_codigo_unico, calcular_precio_total


class TestGenerarCodigo:
    """Tests para la generación de códigos únicos"""
    
    def test_formato_codigo(self):
        """Verifica que el código tenga el formato HK-XXXXX"""
        codigo = generar_codigo_unico()
        assert codigo.startswith("HK-")
        assert len(codigo) == 8  # HK- + 5 caracteres
        assert "-" in codigo
    
    def test_codigo_unico(self):
        """Verifica que los códigos generados sean únicos"""
        codigos = [generar_codigo_unico() for _ in range(100)]
        assert len(set(codigos)) == 100  # Todos únicos


class TestCalcularPrecio:
    """Tests para el cálculo de precios"""
    
    @patch('services.reserva_service.get_db_connection')
    def test_calculo_simple(self, mock_db):
        """Verifica el cálculo básico del precio"""
        # Mock de la conexión
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'precio_noche': 200.0}
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        # 3 noches a $200 = $600
        precio = calcular_precio_total(1, '2025-06-01', '2025-06-04')
        assert precio == 600.0
    
    @patch('services.reserva_service.get_db_connection')
    def test_calculo_con_servicios(self, mock_db):
        """Verifica el cálculo incluyendo servicios extra"""
        # Mock para habitación
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            {'precio_noche': 200.0},  # Precio de habitación
            {'precio': 50.0},         # Precio del servicio extra
            {'precio': 30.0},         # Precio del segundo servicio
        ]
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        # 2 noches a $200 + $50 + $30 = $480
        precio = calcular_precio_total(1, '2025-06-01', '2025-06-03', [1, 2])
        assert precio == 480.0
    
    @patch('services.reserva_service.get_db_connection')
    def test_habitacion_no_encontrada(self, mock_db):
        """Verifica que devuelve None si la habitación no existe"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        precio = calcular_precio_total(999, '2025-06-01', '2025-06-03')
        assert precio is None


if __name__ == '__main__':
    pytest.main([__file__])