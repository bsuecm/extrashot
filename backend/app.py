"""
NDI Controller - Flask Application
A web-based NDI controller for Raspberry Pi
"""
import os
import sys
import logging
import atexit
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import Config
from services.yuri_manager import YuriManager
from services.config_generator import ConfigGenerator
from services.ndi_discovery import NDIDiscoveryService
from services.ptz_controller import PTZController
from routes import sources, viewer, ptz, output

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    CORS(app)

    # Store config
    app.config['app_config'] = config_class

    # Ensure directories exist
    os.makedirs(config_class.CONFIG_DIR, exist_ok=True)

    # Initialize services
    app.config['yuri_manager'] = YuriManager(
        yuri_bin=config_class.YURI_BIN,
        config_dir=config_class.CONFIG_DIR,
        extra_ips_file=config_class.NDI_EXTRA_IPS_FILE,
        lib_path=config_class.YURI_LIB_PATH,
        ndi_lib_path=config_class.NDI_LIB_PATH
    )

    app.config['config_generator'] = ConfigGenerator(
        template_dir=config_class.TEMPLATE_DIR,
        output_dir=config_class.CONFIG_DIR
    )

    app.config['discovery_service'] = NDIDiscoveryService(
        yuri_bin=config_class.YURI_BIN,
        extra_ips_file=config_class.NDI_EXTRA_IPS_FILE,
        lib_path=config_class.YURI_LIB_PATH,
        ndi_lib_path=config_class.NDI_LIB_PATH
    )

    app.config['ptz_controller'] = PTZController(
        control_url=f'http://localhost:{config_class.YURI_WEBSERVER_PORT}/control'
    )

    # Register blueprints
    app.register_blueprint(sources.bp, url_prefix='/api/sources')
    app.register_blueprint(viewer.bp, url_prefix='/api/viewer')
    app.register_blueprint(ptz.bp, url_prefix='/api/ptz')
    app.register_blueprint(output.bp, url_prefix='/api/output')

    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'ok',
            'processes': app.config['yuri_manager'].get_all_status()
        })

    # Serve React frontend (production)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        frontend_dir = config_class.FRONTEND_DIR
        if not os.path.exists(frontend_dir):
            return jsonify({
                'message': 'NDI Controller API',
                'version': '1.0.0',
                'endpoints': {
                    'sources': '/api/sources/',
                    'viewer': '/api/viewer/',
                    'ptz': '/api/ptz/',
                    'output': '/api/output/',
                    'health': '/api/health'
                }
            })

        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, 'index.html')

    # Cleanup on shutdown
    def cleanup():
        logger.info("Shutting down, stopping all yuri processes...")
        app.config['yuri_manager'].stop_all()

    atexit.register(cleanup)

    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    # Run development server
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=True
    )
