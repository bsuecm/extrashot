"""
PTZ Control API Routes
"""
from flask import Blueprint, jsonify, request, current_app

bp = Blueprint('ptz', __name__)


def get_ptz_controller():
    return current_app.config['ptz_controller']


@bp.route('/move', methods=['POST'])
def move():
    """Continuous move with speed"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    pan_speed = float(data.get('pan_speed', 0))
    tilt_speed = float(data.get('tilt_speed', 0))

    success = get_ptz_controller().set_pan_tilt_speed(pan_speed, tilt_speed)
    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/stop', methods=['POST'])
def stop():
    """Stop all movement"""
    success = get_ptz_controller().stop()
    return jsonify({'status': 'stopped' if success else 'failed'})


@bp.route('/position', methods=['POST'])
def set_position():
    """Set absolute pan/tilt position"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    pan = float(data.get('pan', 0))
    tilt = float(data.get('tilt', 0))

    success = get_ptz_controller().set_pan_tilt(pan, tilt)
    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/zoom', methods=['POST'])
def zoom():
    """Set zoom speed or level"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    ptz = get_ptz_controller()

    if 'speed' in data:
        success = ptz.set_zoom_speed(float(data['speed']))
    elif 'level' in data:
        success = ptz.set_zoom(float(data['level']))
    else:
        return jsonify({'error': 'speed or level required'}), 400

    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/preset/recall', methods=['POST'])
def recall_preset():
    """Recall a preset"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    preset = int(data.get('preset', 0))
    speed = float(data.get('speed', 1.0))

    success = get_ptz_controller().recall_preset(preset, speed)
    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/preset/store', methods=['POST'])
def store_preset():
    """Store current position as preset"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    preset = int(data.get('preset', 0))

    success = get_ptz_controller().store_preset(preset)
    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/focus', methods=['POST'])
def focus():
    """Focus control"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    ptz = get_ptz_controller()

    if data.get('auto'):
        success = ptz.auto_focus()
    elif 'speed' in data:
        success = ptz.set_focus_speed(float(data['speed']))
    elif 'level' in data:
        success = ptz.set_focus(float(data['level']))
    else:
        return jsonify({'error': 'auto, speed, or level required'}), 400

    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/whitebalance', methods=['POST'])
def white_balance():
    """White balance control"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    mode = data.get('mode', 'auto')
    ptz = get_ptz_controller()

    if mode == 'auto':
        success = ptz.white_balance_auto()
    elif mode == 'indoor':
        success = ptz.white_balance_indoor()
    elif mode == 'outdoor':
        success = ptz.white_balance_outdoor()
    elif mode == 'oneshot':
        success = ptz.white_balance_oneshot()
    elif mode == 'manual':
        red = float(data.get('red', 0.5))
        blue = float(data.get('blue', 0.5))
        success = ptz.white_balance_manual(red, blue)
    else:
        return jsonify({'error': f'Unknown mode: {mode}'}), 400

    return jsonify({'status': 'ok' if success else 'failed'})


@bp.route('/exposure', methods=['POST'])
def exposure():
    """Exposure control"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    ptz = get_ptz_controller()

    if data.get('auto'):
        success = ptz.exposure_auto()
    elif 'level' in data:
        success = ptz.exposure_manual(float(data['level']))
    else:
        return jsonify({'error': 'auto or level required'}), 400

    return jsonify({'status': 'ok' if success else 'failed'})
