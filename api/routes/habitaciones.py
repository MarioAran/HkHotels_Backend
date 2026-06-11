"""
Rutas para el CRUD de habitaciones (público)
GET  /api/habitaciones       - Listar todas las habitaciones activas
GET  /api/habitaciones/<id>  - Obtener detalle de una habitación
"""
from flask import Blueprint, jsonify, request
from config.database import get_db_connection

habitaciones_bp = Blueprint('habitaciones', __name__)


@habitaciones_bp.route('/habitaciones', methods=['GET'])
def listar_habitaciones():
    """Obtiene todas las habitaciones activas"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, precio_noche, max_personas, descripcion, imagen_url, amenities "
            "FROM habitaciones WHERE activa = TRUE ORDER BY precio_noche ASC"
        )
        habitaciones = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            "success": True,
            "data": [dict(h) for h in habitaciones]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@habitaciones_bp.route('/habitaciones/<int:id>', methods=['GET'])
def obtener_habitacion(id):
    """Obtiene el detalle de una habitación por su ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, precio_noche, max_personas, descripcion, imagen_url, amenities "
            "FROM habitaciones WHERE id = %s AND activa = TRUE",
            (id,)
        )
        habitacion = cursor.fetchone()
        cursor.close()
        
        if not habitacion:
            return jsonify({"success": False, "message": "Habitación no encontrada"}), 404
        
        return jsonify({
            "success": True,
            "data": dict(habitacion)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500