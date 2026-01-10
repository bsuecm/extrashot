"""
NDI Viewer API Routes
"""
from flask import Blueprint, jsonify, request, current_app

bp = Blueprint('viewer', __name__)

VIEWER_PROCESS_NAME = 'viewer'


def get_yuri_manager():
    return current_app.config['yuri_manager']


def get_config_generator():
    return current_app.config['config_generator']


@bp.route('/start', methods=['POST'])
def start_viewer():
    """Start viewing an NDI source"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    source_name = data.get('source')
    if not source_name:
        return jsonify({'error': 'source is required'}), 400

    backup_source = data.get('backup')
    audio = data.get('audio', False)
    fullscreen = data.get('fullscreen', True)
    resolution = data.get('resolution', '1920x1080')

    try:
        config_path = get_config_generator().generate_viewer_config(
            ndi_source=source_name,
            backup_source=backup_source,
            audio_enabled=audio,
            fullscreen=fullscreen,
            resolution=resolution
        )

        result = get_yuri_manager().start_process(VIEWER_PROCESS_NAME, config_path)
        result['source'] = source_name
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stop', methods=['POST'])
def stop_viewer():
    """Stop the viewer"""
    try:
        result = get_yuri_manager().stop_process(VIEWER_PROCESS_NAME)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/switch', methods=['POST'])
def switch_source():
    """Switch to a different NDI source"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    source_name = data.get('source')
    if not source_name:
        return jsonify({'error': 'source is required'}), 400

    backup_source = data.get('backup')
    audio = data.get('audio', False)
    fullscreen = data.get('fullscreen', True)
    resolution = data.get('resolution', '1920x1080')

    try:
        config_path = get_config_generator().generate_viewer_config(
            ndi_source=source_name,
            backup_source=backup_source,
            audio_enabled=audio,
            fullscreen=fullscreen,
            resolution=resolution
        )

        result = get_yuri_manager().restart_process(VIEWER_PROCESS_NAME, config_path)
        result['source'] = source_name
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/status', methods=['GET'])
def viewer_status():
    """Get viewer status"""
    status = get_yuri_manager().get_status(VIEWER_PROCESS_NAME)
    if status is None:
        return jsonify({'running': False, 'name': VIEWER_PROCESS_NAME})
    return jsonify(status)
