"""
Preview Stream API - MJPEG stream for browser preview
Reads JPEG frames from ramdisk written by yuri
"""
import os
import glob
import time
import threading
from flask import Blueprint, Response, jsonify

bp = Blueprint('preview', __name__)

PREVIEW_DIR = '/dev/shm/extrashot_preview'
PREVIEW_PATTERN = os.path.join(PREVIEW_DIR, 'frame_*.jpg')
FRAME_INTERVAL = 0.033  # ~30fps
MAX_FRAMES_TO_KEEP = 5  # Keep only last 5 frames


def get_latest_frame():
    """Get the latest JPEG frame from the preview directory"""
    try:
        files = glob.glob(PREVIEW_PATTERN)
        if not files:
            return None

        # Get the most recently modified file
        latest = max(files, key=os.path.getmtime)
        with open(latest, 'rb') as f:
            return f.read()
    except Exception:
        return None


def cleanup_old_frames():
    """Remove old frame files, keeping only the most recent ones"""
    try:
        files = glob.glob(PREVIEW_PATTERN)
        if len(files) > MAX_FRAMES_TO_KEEP:
            # Sort by modification time
            files.sort(key=os.path.getmtime)
            # Remove oldest files
            for f in files[:-MAX_FRAMES_TO_KEEP]:
                try:
                    os.remove(f)
                except Exception:
                    pass
    except Exception:
        pass


def generate_mjpeg():
    """Generator that yields MJPEG frames from the preview directory"""
    cleanup_counter = 0
    try:
        while True:
            frame = get_latest_frame()
            if frame:
                try:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except GeneratorExit:
                    # Client disconnected - exit gracefully
                    return
                except (BrokenPipeError, ConnectionResetError, OSError):
                    # Connection lost - exit gracefully
                    return

            # Cleanup old frames periodically (every 30 frames)
            cleanup_counter += 1
            if cleanup_counter >= 30:
                cleanup_old_frames()
                cleanup_counter = 0

            time.sleep(FRAME_INTERVAL)
    except GeneratorExit:
        # Client disconnected
        pass
    except Exception:
        # Any other error - exit gracefully rather than crash
        pass


@bp.route('/stream')
def stream():
    """MJPEG stream endpoint"""
    return Response(
        generate_mjpeg(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@bp.route('/snapshot')
def snapshot():
    """Single frame snapshot"""
    frame = get_latest_frame()
    if frame:
        return Response(frame, mimetype='image/jpeg')
    return jsonify({'error': 'No preview available'}), 404


@bp.route('/status')
def status():
    """Check if preview is available"""
    frame = get_latest_frame()
    return jsonify({
        'available': frame is not None
    })
