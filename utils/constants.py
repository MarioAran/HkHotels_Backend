"""
Constantes de la aplicación HK Hotels
"""
# Estados de reserva
ESTADOS_RESERVA = {
    'PENDIENTE': 'pendiente',
    'CONFIRMADA': 'confirmada',
    'CANCELADA': 'cancelada',
    'COMPLETADA': 'completada'
}

# Roles de usuario
ROLES_USUARIO = {
    'SUPER_ADMIN': 'super_admin',
    'ADMIN': 'admin',
    'RECEPCIONISTA': 'recepcionista'
}

# Precios por defecto
PRECIO_MINIMO_HABITACION = 50.0
PRECIO_MAXIMO_HABITACION = 1000.0
HUESPEDES_MINIMO = 1
HUESPEDES_MAXIMO = 10
DIAS_MAXIMOS_RESERVA = 30

# Formato de código de reserva
PREFIJO_CODIGO_RESERVA = "HK-"
LONGITUD_CODIGO_RESERVA = 5

# Imágenes por defecto (Unsplash)
IMAGENES_POR_DEFECTO = {
    'suite_presidencial': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800',
    'suite_ejecutiva': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800',
    'habitacion_deluxe': 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800',
    'habitacion_estandar': 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800',
    'hero': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1920'
}

# Información del hotel
HOTEL_INFO = {
    'nombre': 'HK Hotels',
    'direccion': 'Av. del Mar, 123, 07800 Ibiza, España',
    'telefono': '+34 971 123 456',
    'email': 'info@hkhotels.com',
    'checkin': '15:00',
    'checkout': '12:00'
}