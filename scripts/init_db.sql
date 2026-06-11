-- Script de inicialización de la base de datos PostgreSQL
-- HK Hotels - Base de datos para gestión hotelera

-- Conectar a la base de datos (en Render ya viene creada)
\c hk_hotel_db;

-- Tabla de habitaciones
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
);

-- Tabla de servicios
CREATE TABLE IF NOT EXISTS servicios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    icono VARCHAR(50),
    precio_adicional DECIMAL(10,2) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de reservas
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
);

-- Tabla de usuarios admin
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    nombre_completo VARCHAR(100),
    rol VARCHAR(20) DEFAULT 'recepcionista' CHECK (rol IN ('super_admin', 'admin', 'recepcionista')),
    activo BOOLEAN DEFAULT TRUE
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_reservas_email ON reservas(email);
CREATE INDEX IF NOT EXISTS idx_reservas_codigo ON reservas(codigo_unico);
CREATE INDEX IF NOT EXISTS idx_reservas_fechas ON reservas(fecha_checkin, fecha_checkout);
CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado);
CREATE INDEX IF NOT EXISTS idx_habitaciones_activa ON habitaciones(activa);