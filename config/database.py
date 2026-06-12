"""
Configuración y conexión a la base de datos PostgreSQL
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g
from urllib.parse import urlparse


def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    if 'db' not in g:
        database_url = os.environ.get('DATABASE_URL', '')
        
        if database_url:
            # Parsear DATABASE_URL (formato: postgresql://user:pass@host:port/dbname)
            result = urlparse(database_url)
            g.db = psycopg2.connect(
                host=result.hostname,
                port=result.port or 5432,
                database=result.path[1:],  # Quitar el '/' inicial
                user=result.username,
                password=result.password,
                sslmode='require',
                cursor_factory=RealDictCursor
            )
        else:
            # Fallback a variables individuales
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
    """Inicializa la base de datos, crea tablas y carga datos de ejemplo si está vacía"""
    from scripts.init_db import crear_tablas, seed_data
    
    with app.app_context():
        try:
            conn = get_db_connection()
            crear_tablas(conn)
            conn.commit()
            seed_data(conn)
            conn.commit()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
        finally:
            close_db_connection()
    
    # Registrar la función para cerrar conexión al finalizar cada request
    app.teardown_appcontext(close_db_connection)