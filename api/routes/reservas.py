"""
Rutas para gestión de reservas (público)
POST /api/reservas                    - Crear una nueva reserva
GET  /api/reservas/consultar?email=X  - Consultar reservas por email
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from config.database import get_db_connection
from services.reserva_service import crear_nueva_reserva, consultar_reservas_por_email

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/reservas', methods=['POST'])
def crear_reserva():
    """Crea una nueva reserva en el hotel"""
    datos = request.get_json()
    
    # Validar campos requeridos
    campos_requeridos = ['nombre_cliente', 'email', 'habitacion_id', 'fecha_checkin', 'fecha_checkout', 'huespedes']
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            return jsonify({
                "success": False,
                "message": f"El campo '{campo}' es requerido"
            }), 400
    
    # Validar email
    if '@' not in datos['email'] or '.' not in datos['email']:
        return jsonify({
            "success": False,
            "message": "Email inválido"
        }), 400
    
    # Validar fechas
    try:
        checkin = datetime.strptime(datos['fecha_checkin'], '%Y-%m-%d')
        checkout = datetime.strptime(datos['fecha_checkout'], '%Y-%m-%d')
        
        if checkout <= checkin:
            return jsonify({
                "success": False,
                "message": "La fecha de salida debe ser posterior a la fecha de entrada"
            }), 400
        
        if checkin < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            return jsonify({
                "success": False,
                "message": "La fecha de entrada no puede ser en el pasado"
            }), 400
    
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Formato de fecha inválido. Use YYYY-MM-DD"
        }), 400
    
    # Validar número de huéspedes
    if int(datos['huespedes']) < 1:
        return jsonify({
            "success": False,
            "message": "Debe haber al menos 1 huésped"
        }), 400
    
    try:
        resultado = crear_nueva_reserva(datos)
        if resultado['success']:
            return jsonify(resultado), 201
        return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@reservas_bp.route('/reservas/<int:id>/cancelar', methods=['POST'])
def cancelar_reserva(id):
    """Cancela una reserva por ID (verifica email del cliente)"""
    datos = request.get_json(silent=True) or {}
    email = datos.get('email', '').strip().lower()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener reserva
        cursor.execute(
            "SELECT id, email, estado FROM reservas WHERE id = %s",
            (id,)
        )
        reserva = cursor.fetchone()

        if not reserva:
            cursor.close()
            return jsonify({
                "success": False,
                "message": "Reserva no encontrada"
            }), 404

        # Verificar email
        if reserva['email'].lower() != email:
            cursor.close()
            return jsonify({
                "success": False,
                "message": "El email no coincide con la reserva"
            }), 403

        if reserva['estado'] == 'cancelada':
            cursor.close()
            return jsonify({
                "success": False,
                "message": "La reserva ya está cancelada"
            }), 400

        # Cancelar reserva
        cursor.execute(
            "UPDATE reservas SET estado = 'cancelada' WHERE id = %s",
            (id,)
        )
        conn.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "message": "Reserva cancelada exitosamente",
            "data": {"id": id, "estado": "cancelada"}
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@reservas_bp.route('/reservas/consultar', methods=['GET'])
def consultar_reserva():
    """Consulta reservas por email y opcionalmente por código"""
    email = request.args.get('email')
    codigo = request.args.get('codigo')
    
    if not email:
        return jsonify({
            "success": False,
            "message": "El email es requerido"
        }), 400
    
    try:
        resultado = consultar_reservas_por_email(email, codigo)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500