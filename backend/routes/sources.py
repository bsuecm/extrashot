"""
NDI Sources API Routes
"""
from flask import Blueprint, jsonify, request, current_app

bp = Blueprint('sources', __name__)


def get_discovery_service():
    return current_app.config['discovery_service']


@bp.route('/', methods=['GET'])
def list_sources():
    """List all discovered NDI sources"""
    try:
        sources = get_discovery_service().discover_sources()
        return jsonify({'sources': sources, 'count': len(sources)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/refresh', methods=['POST'])
def refresh_sources():
    """Force refresh of NDI sources"""
    try:
        timeout = request.json.get('timeout', 8) if request.is_json else 8
        sources = get_discovery_service().discover_sources(timeout=timeout)
        return jsonify({'sources': sources, 'count': len(sources)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/extra-ips', methods=['GET'])
def get_extra_ips():
    """Get list of extra IPs for NDI discovery"""
    ips = get_discovery_service().get_extra_ips()
    return jsonify({'ips': ips})


@bp.route('/extra-ips', methods=['PUT'])
def set_extra_ips():
    """Set extra IPs for NDI discovery"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    ips = request.json.get('ips', [])
    if not isinstance(ips, list):
        return jsonify({'error': 'ips must be a list'}), 400

    get_discovery_service().set_extra_ips(ips)
    return jsonify({'ips': ips})


@bp.route('/extra-ips', methods=['POST'])
def add_extra_ip():
    """Add an extra IP for NDI discovery"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    ip = request.json.get('ip')
    if not ip:
        return jsonify({'error': 'ip is required'}), 400

    ips = get_discovery_service().add_extra_ip(ip)
    return jsonify({'ips': ips})


@bp.route('/extra-ips/<ip>', methods=['DELETE'])
def remove_extra_ip(ip):
    """Remove an extra IP from NDI discovery"""
    ips = get_discovery_service().remove_extra_ip(ip)
    return jsonify({'ips': ips})
