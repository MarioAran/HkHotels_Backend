"""
Configuraciones de la aplicación HK Hotels
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración principal de Flask"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Base de datos PostgreSQL - Soporta DATABASE_URL y variables individuales
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '5432')
        DB_NAME = os.environ.get('DB_NAME', 'hk_hotel_db')
        DB_USER = os.environ.get('DB_USER', 'postgres')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
        SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Entorno
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # CORS
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS',
        'https://marioaran.github.io,http://localhost:5000,http://127.0.0.1:5000,http://localhost:5500'
    ).split(',')
