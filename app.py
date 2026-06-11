"""
HK HOTELS - Backend API (Flask + PostgreSQL)
Desplegado en Render: https://hkhotels-backend.onrender.com
"""
import os
from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv
from config.database import init_db
from config.settings import Config
from api.middleware.cors_middleware import configure_cors
from api.routes.habitaciones import habitaciones_bp
from api.routes.reservas import reservas_bp
from api.routes.disponibilidad import disponibilidad_bp
from api.routes.servicios import servicios_bp
from api.routes.auth import auth_bp
from api.routes.admin import admin_bp

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# ============================================
# CONFIGURACIÓN CORS PERSONALIZADA
# - GET: permite cualquier origen
# - POST/PUT/DELETE: solo desde GitHub Pages
# ============================================

# Orígenes permitidos para métodos que no son GET
ALLOWED_ORIGINS = [
    'https://marioaran.github.io',
    'https://marioaran.github.io/HkHotels',
    'http://localhost:3000',   # Desarrollo local React
    'http://localhost:5500',   # Desarrollo local VS Code
    'http://localhost:5000'    # Desarrollo local Flask
]

@app.after_request
def apply_cors(response):
    """Aplica CORS según el método HTTP"""
    origin = request.headers.get('Origin')
    method = request.method
    
    # GET, OPTIONS, HEAD: permitir cualquier origen
    if method in ['GET', 'OPTIONS', 'HEAD']:
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
    else:
        # POST, PUT, DELETE, etc.: solo orígenes permitidos
        environment = os.environ.get('FLASK_ENV', 'development')
        allowed = ALLOWED_ORIGINS.copy()
        
        # En desarrollo, permitir más orígenes
        if environment == 'development':
            allowed.extend([
                'http://localhost:3000',
                'http://localhost:5500',
                'http://localhost:5000'
            ])
        
        if origin in allowed:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = ''
    
    # Headers comunes para todas las respuestas
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    response.headers['Vary'] = 'Origin'
    
    return response

@app.route('/api/<path:path>', methods=['OPTIONS'])
@app.route('/api', methods=['OPTIONS'], defaults={'path': ''})
def handle_options(path):
    """Maneja peticiones OPTIONS (preflight)"""
    response = make_response()
    origin = request.headers.get('Origin')
    
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    
    return response, 200

# ============================================
# FIN CONFIGURACIÓN CORS
# ============================================

# Configurar CORS adicional (si tu middleware tiene más configuraciones)
# configure_cors(app)  # Descomenta si necesitas configuraciones extras

# Inicializar base de datos
init_db(app)

# Registrar blueprints
app.register_blueprint(habitaciones_bp, url_prefix='/api')
app.register_blueprint(reservas_bp, url_prefix='/api')
app.register_blueprint(disponibilidad_bp, url_prefix='/api')
app.register_blueprint(servicios_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Ruta de salud (health check)
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "HK Hotels API funcionando"})

# Manejador de errores 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "Endpoint no encontrado"}), 404

# Manejador de errores 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "message": "Error interno del servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)