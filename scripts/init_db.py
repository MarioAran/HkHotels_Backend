"""
Script Python para inicializar la base de datos
Crea las tablas si no existen y carga datos iniciales
"""
import os
import bcrypt
from config.database import get_db_connection


def crear_tablas(conn):
    """Crea todas las tablas de la base de datos"""
    cursor = conn.cursor()
    
    # Tabla de habitaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habitaciones (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            precio_noche DECIMAL(10,2) NOT NULL,
            max_personas INT NOT NULL,
            descripcion TEXT,
            imagen_url VARCHAR(255),
            amenities JSONB,
            activa BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de servicios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            icono VARCHAR(50),
            precio_adicional DECIMAL(10,2) DEFAULT 0,
            activo BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Tabla de reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id SERIAL PRIMARY KEY,
            codigo_unico VARCHAR(10) UNIQUE NOT NULL,
            nombre_cliente VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            telefono VARCHAR(20),
            habitacion_id INT NOT NULL REFERENCES habitaciones(id),
            fecha_checkin DATE NOT NULL,
            fecha_checkout DATE NOT NULL,
            noches INT GENERATED ALWAYS AS (fecha_checkout - fecha_checkin) STORED,
            huespedes INT NOT NULL,
            servicios_extra JSONB,
            precio_total DECIMAL(10,2) NOT NULL,
            fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada'))
        )
    """)
    
    # Tabla de usuarios admin
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            nombre_completo VARCHAR(100),
            rol VARCHAR(20) DEFAULT 'recepcionista' CHECK (rol IN ('super_admin', 'admin', 'recepcionista')),
            activo BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reservas_email ON reservas(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reservas_codigo ON reservas(codigo_unico)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reservas_fechas ON reservas(fecha_checkin, fecha_checkout)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_habitaciones_activa ON habitaciones(activa)")
    
    cursor.close()
    print("✅ Tablas creadas correctamente")


def seed_data(conn):
    """Inserta datos de ejemplo si las tablas están vacías"""
    cursor = conn.cursor()
    
    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) as count FROM habitaciones")
    count = cursor.fetchone()['count']
    
    if count > 0:
        print("ℹ️  Los datos de ejemplo ya existen, omitiendo seed")
        cursor.close()
        return
    
    # Insertar habitaciones de ejemplo
    cursor.execute("""
        INSERT INTO habitaciones (nombre, precio_noche, max_personas, descripcion, imagen_url, amenities) VALUES
        ('Suite Presidencial', 450.00, 4, 'Vistas al mar, jacuzzi, terraza privada con piscina infinita', 
         'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800',
         '["WiFi", "Jacuzzi", "Terraza", "Minibar", "TV 55\"", "Aire acondicionado", "Caja fuerte"]'),
        ('Suite Ejecutiva', 320.00, 3, 'Sala de estar separada, amenities premium, vistas panorámicas',
         'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800',
         '["WiFi", "Sala estar", "Minibar", "TV 50\"", "Aire acondicionado", "Escritorio"]'),
        ('Habitación Deluxe', 220.00, 2, 'Amplia habitación con cama king size y vistas a la ciudad',
         'https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800',
         '["WiFi", "TV 43\"", "Aire acondicionado", "Caja fuerte", "Secador"]'),
        ('Habitación Estándar', 150.00, 2, 'Cómoda habitación con todas las comodidades básicas',
         'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800',
         '["WiFi", "TV 32\"", "Aire acondicionado", "Baño privado"]')
    """)
    
    # Insertar servicios de ejemplo
    cursor.execute("""
        INSERT INTO servicios (nombre, descripcion, icono, precio_adicional) VALUES
        ('Spa & Wellness', 'Circuito de aguas termales, sauna y masajes relajantes', 'spa-icon', 80.00),
        ('Restaurante Gourmet', 'Cena incluida en restaurante con estrella Michelin', 'restaurant-icon', 60.00),
        ('Traslado Aeropuerto', 'Servicio privado de ida y vuelta al aeropuerto', 'car-icon', 45.00),
        ('Desayuno Buffet', 'Buffet de desayuno internacional cada mañana', 'food-icon', 25.00),
        ('Excursión en Barco', 'Tour privado por la costa con catering incluido', 'boat-icon', 120.00)
    """)
    
    # Crear usuario admin por defecto
    # Password: admin123
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("""
        INSERT INTO usuarios (username, password_hash, email, nombre_completo, rol) VALUES
        ('admin', %s, 'admin@hkhotels.com', 'Administrador HK Hotels', 'super_admin')
    """, (password_hash,))
    
    conn.commit()
    cursor.close()
    print("✅ Datos de ejemplo insertados correctamente")
    print("   Usuario: admin / Contraseña: admin123")