"""
Servicio de lógica de negocio para reservas
Incluye generación de código único, cálculo de precios y creación de reservas
"""
import random
import string
from datetime import datetime
from config.database import get_db_connection


def generar_codigo_unico():
    """Genera un código único para la reserva (formato: HK-XXXXX)"""
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=5))
    return f"HK-{codigo}"


def calcular_precio_total(habitacion_id, fecha_checkin, fecha_checkout, servicios_extra=None):
    """
    Calcula el precio total de la reserva
    - Precio base de la habitación por noche
    - Servicios extra seleccionados
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener precio de la habitación
    cursor.execute(
        "SELECT precio_noche FROM habitaciones WHERE id = %s",
        (habitacion_id,)
    )
    habitacion = cursor.fetchone()
    
    if not habitacion:
        cursor.close()
        return None
    
    precio_noche = float(habitacion['precio_noche'])
    
    # Calcular número de noches
    checkin = datetime.strptime(fecha_checkin, '%Y-%m-%d')
    checkout = datetime.strptime(fecha_checkout, '%Y-%m-%d')
    noches = (checkout - checkin).days
    
    precio_total = precio_noche * noches
    
    # Sumar servicios extra si existen
    if servicios_extra:
        for servicio_id in servicios_extra:
            cursor.execute(
                "SELECT COALESCE(precio_adicional, 0) as precio FROM servicios WHERE id = %s",
                (servicio_id,)
            )
            servicio = cursor.fetchone()
            if servicio:
                precio_total += float(servicio['precio'])
    
    cursor.close()
    return precio_total


def verificar_disponibilidad(habitacion_id, fecha_checkin, fecha_checkout):
    """
    Verifica si una habitación está disponible en el rango de fechas
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM reservas
        WHERE habitacion_id = %s
        AND estado IN ('pendiente', 'confirmada')
        AND NOT (%s >= fecha_checkout OR %s <= fecha_checkin)
    """, (habitacion_id, fecha_checkout, fecha_checkin))
    
    resultado = cursor.fetchone()
    cursor.close()
    
    return resultado['count'] == 0


def crear_nueva_reserva(datos):
    """
    Crea una nueva reserva con toda la lógica de negocio
    """
    # Verificar disponibilidad
    disponible = verificar_disponibilidad(
        datos['habitacion_id'],
        datos['fecha_checkin'],
        datos['fecha_checkout']
    )
    
    if not disponible:
        return {
            "success": False,
            "message": "La habitación no está disponible en las fechas seleccionadas"
        }
    
    # Calcular precio total
    precio_total = calcular_precio_total(
        datos['habitacion_id'],
        datos['fecha_checkin'],
        datos['fecha_checkout'],
        datos.get('servicios_extra', [])
    )
    
    if not precio_total:
        return {
            "success": False,
            "message": "Habitación no encontrada"
        }
    
    # Generar código único
    codigo = generar_codigo_unico()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reservas 
            (codigo_unico, nombre_cliente, email, telefono, habitacion_id, 
             fecha_checkin, fecha_checkout, huespedes, servicios_extra, precio_total, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pendiente')
            RETURNING id, codigo_unico, fecha_reserva
        """, (
            codigo,
            datos['nombre_cliente'],
            datos['email'],
            datos.get('telefono', ''),
            datos['habitacion_id'],
            datos['fecha_checkin'],
            datos['fecha_checkout'],
            int(datos['huespedes']),
            str(datos.get('servicios_extra', [])),
            precio_total
        ))
        
        reserva = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        return {
            "success": True,
            "message": "Reserva creada exitosamente",
            "data": {
                "id": reserva['id'],
                "codigo": reserva['codigo_unico'],
                "precio_total": precio_total,
                "fecha_reserva": reserva['fecha_reserva'].isoformat()
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al crear la reserva: {str(e)}"
        }


def consultar_reservas_por_email(email, codigo=None):
    """
    Consulta reservas por email, opcionalmente filtrado por código
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if codigo:
        cursor.execute("""
            SELECT r.id, r.codigo_unico, r.nombre_cliente, r.email, r.telefono,
                   h.nombre as habitacion_nombre,
                   r.fecha_checkin, r.fecha_checkout, r.huespedes,
                   r.precio_total, r.estado, r.fecha_reserva
            FROM reservas r
            JOIN habitaciones h ON r.habitacion_id = h.id
            WHERE r.email = %s AND r.codigo_unico = %s
            ORDER BY r.fecha_reserva DESC
        """, (email, codigo))
    else:
        cursor.execute("""
            SELECT r.id, r.codigo_unico, r.nombre_cliente, r.email, r.telefono,
                   h.nombre as habitacion_nombre,
                   r.fecha_checkin, r.fecha_checkout, r.huespedes,
                   r.precio_total, r.estado, r.fecha_reserva
            FROM reservas r
            JOIN habitaciones h ON r.habitacion_id = h.id
            WHERE r.email = %s
            ORDER BY r.fecha_reserva DESC
        """, (email,))
    
    reservas = cursor.fetchall()
    cursor.close()
    
    if not reservas:
        return {
            "success": False,
            "message": "No se encontraron reservas"
        }
    
    return {
        "success": True,
        "data": [dict(r) for r in reservas]
    }