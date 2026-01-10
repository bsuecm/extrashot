#!/bin/bash
# NDI Controller Installation Script for Raspberry Pi

set -e

INSTALL_DIR="/opt/ndi-controller"
SERVICE_USER="ndi"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== NDI Controller Installation ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Create service user if not exists
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
    usermod -aG video "$SERVICE_USER"
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/configs/generated"

# Copy backend files
echo "Installing backend..."
cp -r "$PROJECT_DIR/backend/"* "$INSTALL_DIR/"

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install -r "$INSTALL_DIR/requirements.txt"

# Build frontend
echo "Building frontend..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build

# Copy frontend build
echo "Installing frontend..."
cp -r "$PROJECT_DIR/frontend/dist" "$INSTALL_DIR/static"

# Set permissions
echo "Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/app.py"

# Install systemd service
echo "Installing systemd service..."
cp "$SCRIPT_DIR/ndi-controller.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable ndi-controller

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start ndi-controller"
echo "  Stop:    sudo systemctl stop ndi-controller"
echo "  Status:  sudo systemctl status ndi-controller"
echo "  Logs:    sudo journalctl -u ndi-controller -f"
echo ""
echo "The web interface will be available at http://localhost:5000"
echo ""
