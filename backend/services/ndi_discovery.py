"""
NDI Discovery Service - Discovers NDI sources on the network
"""
import subprocess
import os
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NDIDiscoveryService:
    """Discovers NDI sources using ndi_discover tool or yuri2"""

    def __init__(self, yuri_bin: str, extra_ips_file: str,
                 lib_path: str = '/usr/local/lib', ndi_lib_path: str = '/usr/local/lib/libndi.so.6',
                 ndi_discover_bin: str = '/usr/local/bin/ndi_discover'):
        self.yuri_bin = yuri_bin
        self.extra_ips_file = extra_ips_file
        self.lib_path = lib_path
        self.ndi_lib_path = ndi_lib_path
        self.ndi_discover_bin = ndi_discover_bin

    def get_extra_ips(self) -> List[str]:
        """Read extra IPs from file"""
        if os.path.exists(self.extra_ips_file):
            try:
                with open(self.extra_ips_file, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            except Exception as e:
                logger.warning(f"Failed to read extra IPs: {e}")
        return []

    def set_extra_ips(self, ips: List[str]) -> None:
        """Write extra IPs to file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.extra_ips_file), exist_ok=True)
        with open(self.extra_ips_file, 'w') as f:
            f.write('\n'.join(ips))
        logger.info(f"Updated extra IPs: {ips}")

    def add_extra_ip(self, ip: str) -> List[str]:
        """Add an IP to the extra IPs list"""
        ips = self.get_extra_ips()
        if ip not in ips:
            ips.append(ip)
            self.set_extra_ips(ips)
        return ips

    def remove_extra_ip(self, ip: str) -> List[str]:
        """Remove an IP from the extra IPs list"""
        ips = self.get_extra_ips()
        if ip in ips:
            ips.remove(ip)
            self.set_extra_ips(ips)
        return ips

    def _get_env(self) -> dict:
        """Get environment with NDI paths set"""
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{self.lib_path}:{env.get('LD_LIBRARY_PATH', '')}"
        env['NDI_PATH'] = self.ndi_lib_path

        extra_ips = self.get_extra_ips()
        if extra_ips:
            env['NDI_EXTRA_IPS'] = ','.join(extra_ips)
            logger.debug(f"Using extra IPs: {extra_ips}")

        return env

    def discover_sources(self, timeout: int = 8) -> List[Dict]:
        """
        Discover NDI sources using ndi_discover tool.
        Falls back to yuri2 enumerate if ndi_discover is not available.
        Returns list of sources with name and address.
        """
        try:
            logger.info("Starting NDI source discovery...")

            # Try ndi_discover first (preferred method)
            if os.path.exists(self.ndi_discover_bin):
                logger.debug(f"Using ndi_discover: {self.ndi_discover_bin}")
                result = subprocess.run(
                    [self.ndi_discover_bin, '-t', str(timeout)],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 5,  # Extra buffer for tool startup
                    env=self._get_env()
                )
            else:
                # Fallback to yuri2 enumerate
                logger.debug(f"ndi_discover not found, falling back to yuri2")
                result = subprocess.run(
                    [self.yuri_bin, '-I', 'ndi_input'],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=self._get_env()
                )

            logger.debug(f"Discovery stdout: {result.stdout}")
            if result.stderr:
                logger.debug(f"Discovery stderr: {result.stderr}")

            sources = self._parse_enumerate_output(result.stdout)
            logger.info(f"Discovered {len(sources)} NDI sources")
            return sources

        except subprocess.TimeoutExpired:
            logger.warning("NDI discovery timed out")
            return []
        except Exception as e:
            logger.error(f"NDI discovery failed: {e}")
            raise RuntimeError(f"Discovery failed: {e}")

    def _parse_enumerate_output(self, output: str) -> List[Dict]:
        """Parse yuri enumerate output for NDI sources"""
        sources = []

        # Parse format like:
        # Found N devices
        #   Device NAME (Source Name) with 1 configurations
        #   address: IP:PORT

        lines = output.strip().split('\n')
        current_device = None

        for line in lines:
            line = line.strip()

            # Match device line: "Device NAME (Details) with N configurations"
            device_match = re.match(r'Device\s+(.+?)\s+with\s+\d+\s+configuration', line)
            if device_match:
                current_device = {'name': device_match.group(1).strip()}
                continue

            # Match address line: "address: IP:PORT"
            addr_match = re.match(r'address:\s*(.+)', line)
            if addr_match and current_device:
                current_device['address'] = addr_match.group(1).strip()
                sources.append(current_device)
                current_device = None

        return sources
