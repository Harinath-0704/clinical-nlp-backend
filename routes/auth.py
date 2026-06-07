from flask import Blueprint, request, jsonify
from utils.validators import validate_login_payload

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.json or {}
    validate_login_payload(payload)
    return jsonify({'message': 'Login successful', 'user': {'email': payload.get('email')}})

@auth_bp.route('/register', methods=['POST'])
def register():
    payload = request.json or {}
    validate_login_payload(payload)
    return jsonify({'message': 'Registration successful', 'user': {'email': payload.get('email')}})
