# Extrashot

NDI Controller for Raspberry Pi - A web-based interface for NDI source discovery, viewing, output, and PTZ control.

## Features

- **NDI Source Discovery** - Automatically discovers NDI sources on the local network
- **Extra IP Support** - Add IP addresses for discovering NDI sources across subnets/VLANs
- **NDI Viewer** - View NDI sources directly on the Pi's display using yuri2
- **PTZ Control** - Control PTZ-enabled NDI cameras
- **Web Interface** - Modern responsive UI accessible from any browser on the network

## Quick Start (Fresh Install)

For a fresh Raspberry Pi installation, run:

```bash
git clone https://github.com/bsuecm/extrashot.git
cd extrashot
sudo ./scripts/install.sh --full
```

The `--full` flag automatically installs all prerequisites (NDI SDK, yuri2, Node.js, etc.) before installing Extrashot.

## Manual Installation

If you prefer to install prerequisites separately or already have them installed:

### Prerequisites

The following must be installed before running the Extrashot installer:

- **NDI SDK v6** - NDI library for source discovery and streaming
- **yuri2** - Media framework for NDI viewing (built from [libyuri](https://github.com/bsuecm/libyuri))
- **Node.js 20+** - For building the frontend
- **Python 3 with venv** - For the backend API

#### Installing Prerequisites Manually

```bash
# Clone the repo first
git clone https://github.com/bsuecm/extrashot.git
cd extrashot

# Run the prerequisites installer
sudo ./scripts/setup-prerequisites.sh
```

This script will:
- Install system dependencies (build tools, SDL2, ffmpeg libraries)
- Download and install NDI SDK v6
- Clone and build yuri2 from source
- Install Node.js if not present

### Installing Extrashot

Once prerequisites are installed:

```bash
sudo ./scripts/install.sh
```

The installer will:
- Create a service user (`ndi`) with appropriate permissions
- Set up a Python virtual environment with dependencies
- Build and install the frontend
- Configure systemd service for auto-start
- Set up display access for the NDI viewer
- Create necessary directories and permissions

3. Start the service:

```bash
sudo systemctl start ndi-controller
```

## Usage

### Accessing the Web Interface

Open a browser and navigate to:

```
http://<raspberry-pi-ip>:5000
```

### Service Management

```bash
# Start the service
sudo systemctl start ndi-controller

# Stop the service
sudo systemctl stop ndi-controller

# Check status
sudo systemctl status ndi-controller

# View logs
sudo journalctl -u ndi-controller -f
```

### Adding Extra IPs for Cross-Subnet Discovery

NDI discovery typically only works within the same subnet. To discover sources on other networks:

1. Go to the web interface
2. Navigate to Settings
3. Add IP addresses of NDI sources or networks you want to discover
4. The extra IPs are saved to `/opt/ndi-controller/configs/extra_ips.txt`

You can also edit this file directly:

```bash
sudo nano /opt/ndi-controller/configs/extra_ips.txt
```

Add one IP per line, then restart the service:

```bash
sudo systemctl restart ndi-controller
```

## Configuration

### Service Configuration

The systemd service file is located at:
```
/etc/systemd/system/ndi-controller.service
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `YURI_BIN` | Path to yuri2 binary | `/usr/local/bin/yuri2` |
| `NDI_LIB_PATH` | Path to NDI library | `/usr/local/lib/libndi.so.6` |
| `FRONTEND_DIR` | Path to frontend build | `/opt/ndi-controller/frontend/dist` |
| `CONFIG_DIR` | Path to generated configs | `/opt/ndi-controller/configs/generated` |
| `NDI_EXTRA_IPS_FILE` | Path to extra IPs file | `/opt/ndi-controller/configs/extra_ips.txt` |

## Troubleshooting

### Service fails to start after reboot

If you see `NAMESPACE` errors in the logs:

```bash
sudo journalctl -u ndi-controller -n 20
```

The `/dev/shm/extrashot_preview` directory may not exist. The installer creates a tmpfiles.d config to handle this, but you can manually create it:

```bash
sudo mkdir -p /dev/shm/extrashot_preview
sudo chown ndi:ndi /dev/shm/extrashot_preview
sudo systemctl restart ndi-controller
```

### NDI Viewer shows "Authorization required" error

The ndi user needs display access. Run:

```bash
xhost +local:
```

To make this permanent, ensure the xhost autostart entry exists:

```bash
cat ~/.config/autostart/extrashot-xhost.desktop
```

If missing, create it:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/extrashot-xhost.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Extrashot Display Access
Exec=/bin/sh -c "xhost +local:"
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF
```

### NDI sources not discovered

1. Verify NDI library is installed:
   ```bash
   ls -la /usr/local/lib/libndi.so*
   ```

2. Check if sources are on a different subnet and add their IPs to the extra IPs list

3. Ensure firewall allows NDI traffic (TCP/UDP 5960-5970)

## Uninstalling

```bash
sudo ./scripts/uninstall.sh
```

This will stop the service, remove installed files, and optionally remove the service user.

## License

MIT

## Acknowledgments

- [NDI SDK](https://ndi.tv/) by Vizrt
- [Yuri2](https://github.com/iimcz/libyuri) media processing framework
