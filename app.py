import os
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from firebase.firebase_admin import initialize_firebase, verify_jwt_token
from routes.auth import auth_bp
from routes.predict import predict_bp
from routes.patient import patient_bp
from routes.admin import admin_bp
from routes.voice import voice_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'supersecret')

CORS(app,
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

limiter = Limiter(key_func=get_remote_address, default_limits=['100 per hour'])
limiter.init_app(app)

initialize_firebase()

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(predict_bp, url_prefix='/api/predict')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(voice_bp, url_prefix='/api/voice')


@app.before_request
def validate_json_request():
    if request.method in ['POST', 'PUT', 'PATCH'] and request.path.startswith('/api/'):
        if not request.is_json:
            return jsonify({'error': 'Request body must be JSON'}), 400


@app.before_request
def verify_jwt_middleware():
    open_paths = [
        '/api/auth',
        '/api/predict',
        '/api/voice',
        '/api/patient',
        '/api/admin',
    ]

    for path in open_paths:
        if request.path.startswith(path):
            return

    if not request.path.startswith('/api/'):
        return

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing Authorization Bearer token'}), 401

    token = auth_header.split('Bearer ', 1)[1].strip()
    try:
        decoded = verify_jwt_token(token)
        g.firebase_user = decoded
    except Exception as exc:
        return jsonify({'error': str(exc)}), 401


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': str(error)}), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error', 'message': str(error)}), 500


@app.route('/')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Multilingual Clinical NLP Pipeline API running.'
    })


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )