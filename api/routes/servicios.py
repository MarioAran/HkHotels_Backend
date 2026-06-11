"""
Rutas para servicios del hotel (público)
GET /api/servicios - Listar todos los servicios activos
"""
from flask import Blueprint, jsonify
from config.database import get_db_connection

servicios_bp = Blueprint('servicios', __name__)


@servicios_bp.route('/servicios', methods=['GET'])
def listar_servicios():
    """Obtiene todos los servicios activos del hotel"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, descripcion, icono, precio_adicional "
            "FROM servicios WHERE activo = TRUE ORDER BY id ASC"
        )
        servicios = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            "success": True,
            "data": [dict(s) for s in servicios]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500