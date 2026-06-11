"""
Rutas protegidas del panel de administración (requieren token JWT)
"""
from flask import Blueprint, jsonify, request
from config.database import get_db_connection
from config.security import verify_token
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def require_token(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token requerido"}), 401
        
        try:
            token = token.split(' ')[1]  # Bearer <token>
            payload = verify_token(token)
            if not payload:
                return jsonify({"success": False, "message": "Token inválido o expirado"}), 401
            return f(payload, *args, **kwargs)
        except Exception as e:
            return jsonify({"success": False, "message": "Error de autenticación"}), 401
    
    return decorated


# ========= HABITACIONES (CRUD Admin) =========

@admin_bp.route('/admin/habitaciones', methods=['GET'])
@require_token
def listar_habitaciones_admin(payload):
    """Lista todas las habitaciones (incluyendo inactivas)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, precio_noche, max_personas, descripcion, imagen_url, amenities, activa, created_at "
            "FROM habitaciones ORDER BY id DESC"
        )
        habitaciones = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            "success": True,
            "data": [dict(h) for h in habitaciones]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/admin/habitaciones', methods=['POST'])
@require_token
def crear_habitacion_admin(payload):
    """Crea una nueva habitación"""
    datos = request.get_json()
    
    campos_requeridos = ['nombre', 'precio_noche', 'max_personas']
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            return jsonify({"success": False, "message": f"El campo '{campo}' es requerido"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO habitaciones (nombre, precio_noche, max_personas, descripcion, imagen_url, amenities) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (datos['nombre'], float(datos['precio_noche']), int(datos['max_personas']),
             datos.get('descripcion', ''), datos.get('imagen_url', ''), 
             datos.get('amenities', '[]'))
        )
        nueva_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Habitación creada exitosamente",
            "data": {"id": nueva_id}
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/admin/habitaciones/<int:id>', methods=['PUT'])
@require_token
def actualizar_habitacion_admin(payload, id):
    """Actualiza una habitación existente"""
    datos = request.get_json()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        campos_actualizar = []
        valores = []
        
        if 'nombre' in datos:
            campos_actualizar.append("nombre = %s")
            valores.append(datos['nombre'])
        if 'precio_noche' in datos:
            campos_actualizar.append("precio_noche = %s")
            valores.append(float(datos['precio_noche']))
        if 'max_personas' in datos:
            campos_actualizar.append("max_personas = %s")
            valores.append(int(datos['max_personas']))
        if 'descripcion' in datos:
            campos_actualizar.append("descripcion = %s")
            valores.append(datos['descripcion'])
        if 'imagen_url' in datos:
            campos_actualizar.append("imagen_url = %s")
            valores.append(datos['imagen_url'])
        if 'amenities' in datos:
            campos_actualizar.append("amenities = %s")
            valores.append(datos['amenities'])
        if 'activa' in datos:
            campos_actualizar.append("activa = %s")
            valores.append(datos['activa'])
        
        if not campos_actualizar:
            return jsonify({"success": False, "message": "No hay campos para actualizar"}), 400
        
        valores.append(id)
        query = f"UPDATE habitaciones SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Habitación actualizada exitosamente"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/admin/habitaciones/<int:id>', methods=['DELETE'])
@require_token
def eliminar_habitacion_admin(payload, id):
    """Elimina una habitación (borrado lógico)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE habitaciones SET activa = FALSE WHERE id = %s",
            (id,)
        )
        conn.commit()
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Habitación desactivada exitosamente"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ========= SERVICIOS (CRUD Admin) =========

@admin_bp.route('/admin/servicios', methods=['GET'])
@require_token
def listar_servicios_admin(payload):
    """Lista todos los servicios"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, descripcion, icono, precio_adicional, activo "
            "FROM servicios ORDER BY id ASC"
        )
        servicios = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            "success": True,
            "data": [dict(s) for s in servicios]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/admin/servicios', methods=['POST'])
@require_token
def crear_servicio_admin(payload):
    """Crea un nuevo servicio"""
    datos = request.get_json()
    
    if not datos.get('nombre'):
        return jsonify({"success": False, "message": "El nombre del servicio es requerido"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO servicios (nombre, descripcion, icono, precio_adicional) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (datos['nombre'], datos.get('descripcion', ''), datos.get('icono', ''),
             float(datos.get('precio_adicional', 0)))
        )
        nueva_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Servicio creado exitosamente",
            "data": {"id": nueva_id}
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/admin/servicios/<int:id>', methods=['PUT'])
@require_token
def actualizar_servicio_admin(payload, id):
    """Actualiza un servicio existente"""
    datos = request.get_json()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        campos_actualizar = []
        valores = []
        
        for campo in ['nombre', 'descripcion', 'icono', 'precio_adicional', 'activo']:
            if campo in datos:
                campos_actualizar.append(f"{campo} = %s")
                valores.append(datos[campo])
        
        if not campos_actualizar:
            return jsonify({"success": False, "message": "No hay campos para actualizar"}), 400
        
        valores.append(id)
        query = f"UPDATE servicios SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Servicio actualizado exitosamente"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/admin/servicios/<int:id>', methods=['DELETE'])
@require_token
def eliminar_servicio_admin(payload, id):
    """Elimina un servicio (borrado lógico)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE servicios SET activo = FALSE WHERE id = %s",
            (id,)
        )
        conn.commit()
        cursor.close()
        
        return jsonify({
            "success": True,
            "message": "Servicio desactivado exitosamente"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ========= RESERVAS (Admin) =========

@admin_bp.route('/admin/reservas', methods=['GET'])
@require_token
def listar_reservas_admin(payload):
    """Lista todas las reservas del sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.codigo_unico, r.nombre_cliente, r.email, r.telefono,
                   r.habitacion_id, h.nombre as habitacion_nombre,
                   r.fecha_checkin, r.fecha_checkout, r.huespedes,
                   r.precio_total, r.estado, r.fecha_reserva
            FROM reservas r
            JOIN habitaciones h ON r.habitacion_id = h.id
            ORDER BY r.fecha_reserva DESC
        """)
        reservas = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            "success": True,
            "data": [dict(r) for r in reservas]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ========= ESTADÍSTICAS (Admin) =========

@admin_bp.route('/admin/estadisticas', methods=['GET'])
@require_token
def obtener_estadisticas(payload):
    """Obtiene estadísticas del hotel"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de reservas
        cursor.execute("SELECT COUNT(*) as total FROM reservas")
        total_reservas = cursor.fetchone()['total']
        
        # Reservas por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as cantidad 
            FROM reservas GROUP BY estado
        """)
        reservas_estado = {r['estado']: r['cantidad'] for r in cursor.fetchall()}
        
        # Ingresos totales
        cursor.execute("SELECT COALESCE(SUM(precio_total), 0) as total FROM reservas WHERE estado != 'cancelada'")
        ingresos_totales = float(cursor.fetchone()['total'])
        
        # Habitaciones totales
        cursor.execute("SELECT COUNT(*) as total FROM habitaciones WHERE activa = TRUE")
        habitaciones_activas = cursor.fetchone()['total']
        
        cursor.close()
        
        return jsonify({
            "success": True,
            "data": {
                "total_reservas": total_reservas,
                "reservas_por_estado": reservas_estado,
                "ingresos_totales": ingresos_totales,
                "habitaciones_activas": habitaciones_activas
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500