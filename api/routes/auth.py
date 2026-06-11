"""
Rutas de autenticación para el panel de administración
POST /api/auth/login - Iniciar sesión (obtener token JWT)
"""
from flask import Blueprint, jsonify, request
from config.database import get_db_connection
from config.security import verify_password, generate_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Autentica un usuario administrador y devuelve un token JWT"""
    datos = request.get_json()
    
    if not datos or not datos.get('username') or not datos.get('password'):
        return jsonify({
            "success": False,
            "message": "Usuario y contraseña requeridos"
        }), 400
    
    username = datos['username']
    password = datos['password']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, nombre_completo, email, rol "
            "FROM usuarios WHERE username = %s AND activo = TRUE",
            (username,)
        )
        usuario = cursor.fetchone()
        cursor.close()
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Credenciales inválidas"
            }), 401
        
        if not verify_password(password, usuario['password_hash']):
            return jsonify({
                "success": False,
                "message": "Credenciales inválidas"
            }), 401
        
        # Generar token JWT
        token = generate_token(usuario['id'], usuario['username'], usuario['rol'])
        
        return jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso",
            "data": {
                "token": token,
                "usuario": {
                    "id": usuario['id'],
                    "username": usuario['username'],
                    "nombre_completo": usuario['nombre_completo'],
                    "email": usuario['email'],
                    "rol": usuario['rol']
                }
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500