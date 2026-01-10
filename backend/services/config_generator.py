"""
Config Generator - Generates yuri XML configs from templates
"""
import os
from jinja2 import Environment, FileSystemLoader
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ConfigGenerator:
    """Generates yuri XML configuration files from Jinja2 templates"""

    def __init__(self, template_dir: str, output_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_viewer_config(
        self,
        ndi_source: str,
        backup_source: Optional[str] = None,
        audio_enabled: bool = False,
        fullscreen: bool = True,
        resolution: str = '1920x1080'
    ) -> str:
        """Generate NDI viewer XML config"""
        template = self.env.get_template('viewer.xml.j2')
        config = template.render(
            ndi_source=ndi_source,
            backup_source=backup_source or '',
            audio_enabled='true' if audio_enabled else 'false',
            fullscreen='true' if fullscreen else 'false',
            resolution=resolution
        )

        output_path = os.path.join(self.output_dir, 'viewer.xml')
        with open(output_path, 'w') as f:
            f.write(config)

        logger.info(f"Generated viewer config: {output_path}")
        return output_path

    def generate_v4l2_output_config(
        self,
        device_path: str = '/dev/video0',
        output_name: str = 'RaspberryPi-NDI',
        resolution: str = '1920x1080',
        fps: int = 30,
        ptz_enabled: bool = False
    ) -> str:
        """Generate V4L2 to NDI output XML config"""
        template = self.env.get_template('output_v4l2.xml.j2')
        config = template.render(
            device_path=device_path,
            output_name=output_name,
            resolution=resolution,
            fps=fps,
            ptz_enabled='true' if ptz_enabled else 'false'
        )

        output_path = os.path.join(self.output_dir, 'output_v4l2.xml')
        with open(output_path, 'w') as f:
            f.write(config)

        logger.info(f"Generated V4L2 output config: {output_path}")
        return output_path

    def generate_libcamera_output_config(
        self,
        output_name: str = 'RaspberryPi-PiCam',
        resolution: str = '1920x1080',
        fps: int = 30,
        ptz_enabled: bool = False
    ) -> str:
        """Generate libcamera (Pi Camera) to NDI output XML config"""
        template = self.env.get_template('output_libcamera.xml.j2')
        config = template.render(
            output_name=output_name,
            resolution=resolution,
            fps=fps,
            ptz_enabled='true' if ptz_enabled else 'false'
        )

        output_path = os.path.join(self.output_dir, 'output_libcamera.xml')
        with open(output_path, 'w') as f:
            f.write(config)

        logger.info(f"Generated libcamera output config: {output_path}")
        return output_path
