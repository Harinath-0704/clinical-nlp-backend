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

    # Try JSON file first (local development)
    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        # Use environment variables (production on Render)
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
        cred = credentials.Certificate({
            'type': 'service_account',
            'project_id': os.getenv('FIREBASE_PROJECT_ID'),
            'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': private_key,
            'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
            'client_id': os.getenv('FIREBASE_CLIENT_ID'),
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
        })

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