"""
PTZ Controller - Sends PTZ commands to yuri via WebControlResource
"""
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PTZController:
    """
    Sends PTZ commands to yuri via WebControlResource.

    Supported commands (from NDIInput.cpp):
    - pan_tilt: vector [pan, tilt] (-1.0 to 1.0)
    - pan: float (-1.0 to 1.0)
    - tilt: float (-1.0 to 1.0)
    - pan_tilt_speed: vector [pan_speed, tilt_speed] (-1.0 to 1.0)
    - pan_speed: float (-1.0 to 1.0)
    - tilt_speed: float (-1.0 to 1.0)
    - zoom: float (0.0 to 1.0)
    - zoom_speed: float (-1.0 to 1.0)
    - focus: float (0.0 to 1.0)
    - focus_speed: float (-1.0 to 1.0)
    - auto_focus: trigger
    - recall_preset: int or vector [preset_num, speed]
    - store_preset: int
    - white_balance_auto: trigger
    - white_balance_indoor: trigger
    - white_balance_outdoor: trigger
    - white_balance_oneshot: trigger
    - white_balance_manual: vector [red_val, blue_val]
    - exposure_auto: trigger
    - exposure_manual: float
    """

    def __init__(self, control_url: str = 'http://localhost:8080/control'):
        self.control_url = control_url

    def set_control_url(self, url: str):
        """Update the control URL"""
        self.control_url = url

    def _send_command(self, command: str, value: Optional[str] = None) -> bool:
        """Send a PTZ command via yuri's WebControlResource"""
        try:
            params = {command: value if value is not None else ''}
            logger.debug(f"Sending PTZ command: {command}={value}")
            response = requests.get(self.control_url, params=params, timeout=2)
            return response.status_code in (200, 302, 303)
        except requests.RequestException as e:
            logger.warning(f"PTZ command failed: {e}")
            return False

    # Position commands (absolute)
    def set_pan_tilt(self, pan: float, tilt: float) -> bool:
        """Set absolute pan/tilt position (-1.0 to 1.0)"""
        return self._send_command('pan_tilt', f'[{pan},{tilt}]')

    def set_pan(self, pan: float) -> bool:
        """Set absolute pan position (-1.0 to 1.0)"""
        return self._send_command('pan', str(pan))

    def set_tilt(self, tilt: float) -> bool:
        """Set absolute tilt position (-1.0 to 1.0)"""
        return self._send_command('tilt', str(tilt))

    # Speed commands (for continuous movement)
    def set_pan_tilt_speed(self, pan_speed: float, tilt_speed: float) -> bool:
        """Set pan/tilt speed (-1.0 to 1.0, 0 = stop)"""
        return self._send_command('pan_tilt_speed', f'[{pan_speed},{tilt_speed}]')

    def set_pan_speed(self, speed: float) -> bool:
        """Set pan speed (-1.0 to 1.0)"""
        return self._send_command('pan_speed', str(speed))

    def set_tilt_speed(self, speed: float) -> bool:
        """Set tilt speed (-1.0 to 1.0)"""
        return self._send_command('tilt_speed', str(speed))

    def stop(self) -> bool:
        """Stop all movement"""
        success = self.set_pan_tilt_speed(0, 0)
        success = self._send_command('zoom_speed', '0') and success
        return success

    # Zoom
    def set_zoom(self, zoom: float) -> bool:
        """Set zoom level (0.0 to 1.0)"""
        return self._send_command('zoom', str(zoom))

    def set_zoom_speed(self, speed: float) -> bool:
        """Set zoom speed (-1.0 to 1.0)"""
        return self._send_command('zoom_speed', str(speed))

    # Focus
    def set_focus(self, focus: float) -> bool:
        """Set focus level (0.0 to 1.0)"""
        return self._send_command('focus', str(focus))

    def set_focus_speed(self, speed: float) -> bool:
        """Set focus speed (-1.0 to 1.0)"""
        return self._send_command('focus_speed', str(speed))

    def auto_focus(self) -> bool:
        """Trigger automatic focus"""
        return self._send_command('auto_focus')

    # Presets
    def recall_preset(self, preset_num: int, speed: float = 1.0) -> bool:
        """Recall a stored preset"""
        return self._send_command('recall_preset', f'[{preset_num},{speed}]')

    def store_preset(self, preset_num: int) -> bool:
        """Store current position as preset"""
        return self._send_command('store_preset', str(preset_num))

    # White balance
    def white_balance_auto(self) -> bool:
        """Set automatic white balance"""
        return self._send_command('white_balance_auto')

    def white_balance_indoor(self) -> bool:
        """Set indoor white balance preset"""
        return self._send_command('white_balance_indoor')

    def white_balance_outdoor(self) -> bool:
        """Set outdoor white balance preset"""
        return self._send_command('white_balance_outdoor')

    def white_balance_oneshot(self) -> bool:
        """Trigger one-shot white balance"""
        return self._send_command('white_balance_oneshot')

    def white_balance_manual(self, red: float, blue: float) -> bool:
        """Set manual white balance values"""
        return self._send_command('white_balance_manual', f'[{red},{blue}]')

    # Exposure
    def exposure_auto(self) -> bool:
        """Set automatic exposure"""
        return self._send_command('exposure_auto')

    def exposure_manual(self, exposure: float) -> bool:
        """Set manual exposure level"""
        return self._send_command('exposure_manual', str(exposure))
