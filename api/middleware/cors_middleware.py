"""
Middleware de CORS para permitir peticiones desde GitHub Pages
Configurado para producción: https://hkhotels.github.io
"""
import os
from flask_cors import CORS


def configure_cors(app):
    """
    Configura CORS para permitir peticiones del frontend en GitHub Pages
    y orígenes locales para desarrollo
    """
    origins = os.environ.get(
        'CORS_ORIGINS',
        'https://hkhotels.github.io'
    ).split(',')
    
    CORS(app,
         origins=origins,
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    
    print(f"✅ CORS configurado para orígenes: {origins}")