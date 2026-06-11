"""
Configuración de seguridad: CORS, JWT y encriptación
"""
import os
import bcrypt
import jwt
from datetime import datetime, timedelta


# Orígenes permitidos para CORS (producción)
CORS_ORIGINS = [
    "https://hkhotels.github.io",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5500"
]


def hash_password(password):
    """Genera un hash seguro de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, password_hash):
    """Verifica una contraseña contra su hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token(user_id, username, role):
    """Genera un token JWT para el usuario"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    secret = os.environ.get('SECRET_KEY', 'dev-secret-key')
    return jwt.encode(payload, secret, algorithm='HS256')


def verify_token(token):
    """Verifica y decodifica un token JWT"""
    try:
        secret = os.environ.get('SECRET_KEY', 'dev-secret-key')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None