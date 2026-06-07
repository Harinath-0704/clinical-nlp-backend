import os
import functools
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials, firestore
from flask import request, g, abort

firebase_app = None


def initialize_firebase():
    global firebase_app
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        import base64
        import json
        b64 = os.getenv('FIREBASE_CREDENTIALS_BASE64', '')
        cred_dict = json.loads(base64.b64decode(b64).decode())
        cred = credentials.Certificate(cred_dict)

    firebase_app = firebase_admin.initialize_app(cred)
    return firebase_app


def get_firestore():
    return firestore.client()


def get_storage():
    return None


def verify_jwt_token(token):
    try:
        return firebase_auth.verify_id_token(token)
    except Exception as exc:
        abort(401, description=f'Invalid or expired token: {exc}')


def verify_jwt_middleware(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            abort(401, description='Authorization header missing or malformed')
        id_token = auth_header.split('Bearer ')[1].strip()
        decoded_token = verify_jwt_token(id_token)
        g.firebase_user = decoded_token
        return f(*args, **kwargs)
    return wrapper


def require_admin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user = getattr(g, 'firebase_user', {})
        if user.get('role') != 'admin':
            abort(403, description='Admin privileges required')
        return f(*args, **kwargs)
    return wrapper