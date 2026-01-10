"""
NDI Output API Routes
"""
from flask import Blueprint, jsonify, request, current_app
import subprocess
import re

bp = Blueprint('output', __name__)

OUTPUT_PROCESS_NAME = 'output'


def get_yuri_manager():
    return current_app.config['yuri_manager']


def get_config_generator():
    return current_app.config['config_generator']


def get_config():
    return current_app.config['app_config']


@bp.route('/start', methods=['POST'])
def start_output():
    """Start NDI output from camera"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json
    source_type = data.get('source_type') or data.get('type', 'v4l2')  # 'v4l2' or 'libcamera'
    device_path = data.get('device', get_config().DEFAULT_VIDEO_DEVICE)
    output_name = data.get('name', get_config().DEFAULT_NDI_OUTPUT_NAME)

    # Handle resolution as string or width/height
    if 'resolution' in data:
        resolution = data['resolution']
    elif 'width' in data and 'height' in data:
        resolution = f"{data['width']}x{data['height']}"
    else:
        resolution = get_config().DEFAULT_RESOLUTION

    fps = int(data.get('fps', get_config().DEFAULT_FPS))
    ptz_enabled = data.get('ptz', False)

    try:
        config_gen = get_config_generator()

        if source_type == 'libcamera':
            config_path = config_gen.generate_libcamera_output_config(
                output_name=output_name,
                resolution=resolution,
                fps=fps,
                ptz_enabled=ptz_enabled
            )
        else:
            config_path = config_gen.generate_v4l2_output_config(
                device_path=device_path,
                output_name=output_name,
                resolution=resolution,
                fps=fps,
                ptz_enabled=ptz_enabled
            )

        result = get_yuri_manager().start_process(OUTPUT_PROCESS_NAME, config_path)
        result['output_name'] = output_name
        result['source_type'] = source_type
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stop', methods=['POST'])
def stop_output():
    """Stop NDI output"""
    try:
        result = get_yuri_manager().stop_process(OUTPUT_PROCESS_NAME)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/status', methods=['GET'])
def output_status():
    """Get output status"""
    status = get_yuri_manager().get_status(OUTPUT_PROCESS_NAME)
    if status is None:
        return jsonify({'running': False, 'name': OUTPUT_PROCESS_NAME})
    return jsonify(status)


@bp.route('/devices', methods=['GET'])
def list_devices():
    """List available video devices"""
    devices = []

    # List V4L2 devices
    try:
        result = subprocess.run(
            ['v4l2-ctl', '--list-devices'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            current_name = None

            for line in lines:
                if not line.startswith('\t') and line.strip():
                    current_name = line.strip().rstrip(':')
                elif line.startswith('\t') and '/dev/video' in line:
                    device_path = line.strip()
                    devices.append({
                        'path': device_path,
                        'name': current_name or device_path,
                        'type': 'v4l2'
                    })
    except Exception:
        pass

    # Check for Pi Camera via libcamera
    try:
        result = subprocess.run(
            ['libcamera-hello', '--list-cameras'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and 'Available cameras' in result.stdout:
            # Parse camera info
            for match in re.finditer(r'(\d+)\s*:\s*(\w+)', result.stdout):
                devices.append({
                    'path': f'/dev/video{match.group(1)}',
                    'name': f'Pi Camera ({match.group(2)})',
                    'type': 'libcamera'
                })
    except Exception:
        pass

    return jsonify({'devices': devices})
