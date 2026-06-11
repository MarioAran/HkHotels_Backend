"""
Modelo base para la aplicación HK Hotels
Proporciona métodos comunes para interactuar con la base de datos
"""
from config.database import get_db_connection


class BaseModel:
    """Clase base para modelos de datos"""
    
    @staticmethod
    def fetch_all(query, params=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return [dict(r) for r in results]
    
    @staticmethod
    def fetch_one(query, params=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        return dict(result) if result else None
    
    @staticmethod
    def execute(query, params=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()