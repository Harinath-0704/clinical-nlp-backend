from flask import abort


def validate_login_payload(payload):
    email = payload.get('email')
    password = payload.get('password')

    if not email or not password:
        abort(400, description='Email and password are required')

    if '@' not in email:
        abort(400, description='Invalid email address')

    return True
