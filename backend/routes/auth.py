"""
Authentication Routes - Login, logout, and credential management
"""
from flask import Blueprint, jsonify, request, current_app
from functools import wraps

bp = Blueprint('auth', __name__)


def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.cookies.get('auth_token')

        auth_service = current_app.config['auth_service']
        username = auth_service.validate_session(token)

        if not username:
            return jsonify({'error': 'Unauthorized'}), 401

        return f(*args, **kwargs)
    return decorated


@bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return session token"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    auth_service = current_app.config['auth_service']
    token = auth_service.authenticate(username, password)

    if token:
        response = jsonify({
            'success': True,
            'token': token,
            'username': username
        })
        response.set_cookie('auth_token', token, httponly=True, samesite='Lax', max_age=86400)
        return response

    return jsonify({'error': 'Invalid credentials'}), 401


@bp.route('/logout', methods=['POST'])
def logout():
    """Invalidate session token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.cookies.get('auth_token')

    auth_service = current_app.config['auth_service']
    auth_service.logout(token)

    response = jsonify({'success': True})
    response.delete_cookie('auth_token')
    return response


@bp.route('/status')
def status():
    """Check authentication status"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.cookies.get('auth_token')

    auth_service = current_app.config['auth_service']
    username = auth_service.validate_session(token)

    return jsonify({
        'authenticated': username is not None,
        'username': username
    })


@bp.route('/credentials', methods=['PUT'])
@require_auth
def change_credentials():
    """Change username and/or password"""
    data = request.get_json() or {}
    new_username = data.get('username')
    new_password = data.get('password')
    current_password = data.get('current_password')

    if not current_password:
        return jsonify({'error': 'Current password required'}), 400

    if not new_username and not new_password:
        return jsonify({'error': 'New username or password required'}), 400

    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.cookies.get('auth_token')

    auth_service = current_app.config['auth_service']
    result = auth_service.change_credentials(token, new_username, new_password, current_password)

    if result['success']:
        return jsonify(result)
    return jsonify(result), 400
