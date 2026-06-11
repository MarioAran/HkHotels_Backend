"""
Rutas para verificar disponibilidad de habitaciones
GET /api/disponibilidad?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD&habitacion_id=X
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from config.database import get_db_connection

disponibilidad_bp = Blueprint('disponibilidad', __name__)


@disponibilidad_bp.route('/disponibilidad', methods=['GET'])
def check_disponibilidad():
    """Verifica la disponibilidad de habitaciones en un rango de fechas"""
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    habitacion_id = request.args.get('habitacion_id')
    
    # Validar fechas requeridas
    if not fecha_inicio or not fecha_fin:
        return jsonify({
            "success": False,
            "message": "Se requieren fecha_inicio y fecha_fin"
        }), 400
    
    # Validar formato de fechas
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        if fecha_fin_dt <= fecha_inicio_dt:
            return jsonify({
                "success": False,
                "message": "La fecha de salida debe ser posterior a la fecha de entrada"
            }), 400
        
        if fecha_inicio_dt < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            return jsonify({
                "success": False,
                "message": "La fecha de entrada no puede ser en el pasado"
            }), 400
    
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Formato de fecha inválido. Use YYYY-MM-DD"
        }), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if habitacion_id:
            # Verificar disponibilidad de una habitación específica
            cursor.execute("""
                SELECT id, nombre, precio_noche, max_personas, descripcion, imagen_url
                FROM habitaciones
                WHERE id = %s AND activa = TRUE
                AND id NOT IN (
                    SELECT habitacion_id FROM reservas
                    WHERE estado IN ('pendiente', 'confirmada')
                    AND NOT (%s >= fecha_checkout OR %s <= fecha_checkin)
                )
            """, (habitacion_id, fecha_fin, fecha_inicio))
            
            habitacion = cursor.fetchone()
            cursor.close()
            
            if not habitacion:
                return jsonify({
                    "success": False,
                    "message": "Habitación no disponible en esas fechas"
                }), 404
            
            return jsonify({
                "success": True,
                "data": dict(habitacion),
                "disponible": True
            })
        else:
            # Listar todas las habitaciones disponibles
            cursor.execute("""
                SELECT id, nombre, precio_noche, max_personas, descripcion, imagen_url
                FROM habitaciones
                WHERE activa = TRUE
                AND id NOT IN (
                    SELECT habitacion_id FROM reservas
                    WHERE estado IN ('pendiente', 'confirmada')
                    AND NOT (%s >= fecha_checkout OR %s <= fecha_checkin)
                )
                ORDER BY precio_noche ASC
            """, (fecha_fin, fecha_inicio))
            
            habitaciones = cursor.fetchall()
            cursor.close()
            
            return jsonify({
                "success": True,
                "data": [dict(h) for h in habitaciones]
            })
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500