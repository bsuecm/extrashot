"""
NDI Controller Configuration
"""
import os

class Config:
    # Yuri paths
    YURI_BIN = os.environ.get('YURI_BIN', '/usr/local/bin/yuri2')
    YURI_LIB_PATH = os.environ.get('YURI_LIB_PATH', '/usr/local/lib')
    NDI_LIB_PATH = os.environ.get('NDI_LIB_PATH', '/usr/local/lib/libndi.so.6')

    # Directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.environ.get('CONFIG_DIR', os.path.join(BASE_DIR, 'configs', 'generated'))
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    FRONTEND_DIR = os.environ.get('FRONTEND_DIR', os.path.join(BASE_DIR, 'frontend', 'dist'))

    # NDI settings
    NDI_EXTRA_IPS_FILE = os.environ.get('NDI_EXTRA_IPS_FILE', os.path.join(BASE_DIR, 'configs', 'extra_ips.txt'))

    # Server settings
    FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
    YURI_WEBSERVER_PORT = int(os.environ.get('YURI_WEBSERVER_PORT', 8080))

    # Default NDI output settings
    DEFAULT_NDI_OUTPUT_NAME = os.environ.get('DEFAULT_NDI_OUTPUT_NAME', 'RaspberryPi-NDI')
    DEFAULT_VIDEO_DEVICE = os.environ.get('DEFAULT_VIDEO_DEVICE', '/dev/video0')
    DEFAULT_RESOLUTION = os.environ.get('DEFAULT_RESOLUTION', '1280x720')
    DEFAULT_FPS = int(os.environ.get('DEFAULT_FPS', 30))
