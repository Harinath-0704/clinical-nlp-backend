import jwt
from datetime import datetime, timedelta
from flask import current_app


def generate_jwt(payload, expires_in=3600):
    secret_key = current_app.config.get('SECRET_KEY')
    payload_data = payload.copy()
    payload_data['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
    token = jwt.encode(payload_data, secret_key, algorithm='HS256')
    return token


def decode_jwt(token):
    secret_key = current_app.config.get('SECRET_KEY')
    return jwt.decode(token, secret_key, algorithms=['HS256'])
