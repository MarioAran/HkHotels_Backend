"""
HK HOTELS - Backend API (Flask + PostgreSQL)
Desplegado en Render: https://hkhotels-backend.onrender.com
"""
import os
from flask import Flask, jsonify
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

# Configurar CORS
configure_cors(app)

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