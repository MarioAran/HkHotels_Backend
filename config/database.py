"""
Configuración y conexión a la base de datos PostgreSQL
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g


def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            database=os.environ.get('DB_NAME', 'hk_hotel_db'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', ''),
            cursor_factory=RealDictCursor
        )
    return g.db


def close_db_connection(error=None):
    """Cierra la conexión a la base de datos"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """Inicializa la base de datos y crea las tablas si no existen"""
    from scripts.init_db import crear_tablas
    
    with app.app_context():
        try:
            conn = get_db_connection()
            crear_tablas(conn)
            conn.commit()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
        finally:
            close_db_connection()
    
    # Registrar la función para cerrar conexión al finalizar cada request
    app.teardown_appcontext(close_db_connection)