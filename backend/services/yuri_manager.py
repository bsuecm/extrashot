"""
Yuri Process Manager - Manages yuri2 process lifecycle
"""
import subprocess
import os
import signal
import time
import glob
import shutil
from typing import Optional, Dict
from threading import Lock
import logging

logger = logging.getLogger(__name__)

PREVIEW_DIR = '/dev/shm/extrashot_preview'


class YuriProcess:
    """Represents a running yuri process"""
    def __init__(self, name: str, config_path: str, process: subprocess.Popen):
        self.name = name
        self.config_path = config_path
        self.process = process
        self.started_at = time.time()

    @property
    def is_running(self) -> bool:
        return self.process.poll() is None

    @property
    def uptime(self) -> float:
        return time.time() - self.started_at


class YuriManager:
    """Manages multiple yuri processes"""

    def __init__(self, yuri_bin: str, config_dir: str, extra_ips_file: str,
                 lib_path: str = '/usr/local/lib', ndi_lib_path: str = '/usr/local/lib/libndi.so.6'):
        self.yuri_bin = yuri_bin
        self.config_dir = config_dir
        self.extra_ips_file = extra_ips_file
        self.lib_path = lib_path
        self.ndi_lib_path = ndi_lib_path
        self.processes: Dict[str, YuriProcess] = {}
        self.lock = Lock()

        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)

    def _get_env(self) -> dict:
        """Get environment with NDI paths set"""
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{self.lib_path}:{env.get('LD_LIBRARY_PATH', '')}"
        env['NDI_PATH'] = self.ndi_lib_path

        # Add extra IPs for NDI discovery
        if os.path.exists(self.extra_ips_file):
            try:
                with open(self.extra_ips_file, 'r') as f:
                    ips = [line.strip() for line in f if line.strip()]
                    if ips:
                        env['NDI_EXTRA_IPS'] = ','.join(ips)
            except Exception as e:
                logger.warning(f"Failed to read extra IPs: {e}")

        return env

    def _setup_preview_dir(self):
        """Create and clean the preview directory"""
        try:
            # Clean up any existing files
            if os.path.exists(PREVIEW_DIR):
                shutil.rmtree(PREVIEW_DIR)
            os.makedirs(PREVIEW_DIR, exist_ok=True)
            logger.info(f"Created preview directory: {PREVIEW_DIR}")
        except Exception as e:
            logger.warning(f"Failed to setup preview directory: {e}")

    def _cleanup_preview_dir(self):
        """Clean up preview directory"""
        try:
            if os.path.exists(PREVIEW_DIR):
                shutil.rmtree(PREVIEW_DIR)
                logger.info(f"Cleaned up preview directory: {PREVIEW_DIR}")
        except Exception as e:
            logger.warning(f"Failed to cleanup preview directory: {e}")

    def start_process(self, name: str, config_path: str) -> Dict:
        """Start a yuri process with given config"""
        with self.lock:
            # Stop existing process with same name
            if name in self.processes:
                self._stop_process_internal(name)

            # Setup preview directory for output processes
            if 'output' in name.lower():
                self._setup_preview_dir()

            try:
                logger.info(f"Starting yuri process '{name}' with config: {config_path}")
                process = subprocess.Popen(
                    [self.yuri_bin, '-f', config_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=self._get_env()
                )

                # Brief wait to check if it started successfully
                time.sleep(0.5)
                if process.poll() is not None:
                    stderr = process.stderr.read().decode() if process.stderr else ''
                    raise RuntimeError(f"Process exited immediately: {stderr}")

                self.processes[name] = YuriProcess(name, config_path, process)
                logger.info(f"Started yuri process '{name}' with PID {process.pid}")

                return {
                    'status': 'started',
                    'name': name,
                    'pid': process.pid,
                    'config': config_path
                }
            except Exception as e:
                logger.error(f"Failed to start yuri process '{name}': {e}")
                raise RuntimeError(f"Failed to start yuri: {e}")

    def _stop_process_internal(self, name: str) -> bool:
        """Internal stop without lock (called from within locked context)"""
        if name not in self.processes:
            return False

        proc = self.processes[name]
        try:
            logger.info(f"Stopping yuri process '{name}' (PID {proc.process.pid})")
            proc.process.send_signal(signal.SIGTERM)
            proc.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning(f"Process '{name}' did not stop gracefully, killing")
            proc.process.kill()
            proc.process.wait(timeout=2)
        except Exception as e:
            logger.error(f"Error stopping process '{name}': {e}")

        # Cleanup preview directory for output processes
        if 'output' in name.lower():
            self._cleanup_preview_dir()

        del self.processes[name]
        return True

    def stop_process(self, name: str) -> Dict:
        """Stop a running yuri process"""
        with self.lock:
            if name not in self.processes:
                return {'status': 'not_running', 'name': name}

            self._stop_process_internal(name)
            return {'status': 'stopped', 'name': name}

    def restart_process(self, name: str, new_config: Optional[str] = None) -> Dict:
        """Restart a process, optionally with new config"""
        with self.lock:
            if name not in self.processes:
                return {'status': 'error', 'error': f"Process '{name}' not found"}

            config = new_config or self.processes[name].config_path
            self._stop_process_internal(name)

        # Start outside lock to avoid holding it during startup
        return self.start_process(name, config)

    def get_status(self, name: str) -> Optional[Dict]:
        """Get status of a process"""
        with self.lock:
            if name not in self.processes:
                return None

            proc = self.processes[name]
            return {
                'name': name,
                'running': proc.is_running,
                'pid': proc.process.pid if proc.is_running else None,
                'config': proc.config_path,
                'uptime': proc.uptime
            }

    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all processes"""
        with self.lock:
            return {
                name: {
                    'name': name,
                    'running': proc.is_running,
                    'pid': proc.process.pid if proc.is_running else None,
                    'config': proc.config_path,
                    'uptime': proc.uptime
                }
                for name, proc in self.processes.items()
            }

    def stop_all(self):
        """Stop all running processes"""
        with self.lock:
            names = list(self.processes.keys())
            for name in names:
                self._stop_process_internal(name)
