#!/bin/bash
# NDI Controller Installation Script for Raspberry Pi
# This script installs the NDI Controller (Extrashot) as a systemd service

set -e

INSTALL_DIR="/opt/ndi-controller"
SERVICE_USER="ndi"
SERVICE_NAME="ndi-controller"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=========================================="
echo "   NDI Controller (Extrashot) Installer"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    log_error "Python 3 is required but not installed"
    exit 1
fi

if ! command -v yuri2 &>/dev/null; then
    log_warn "yuri2 not found in PATH. Make sure it's installed at /usr/local/bin/yuri2"
fi

if [ ! -f "/usr/local/lib/libndi.so.6" ] && [ ! -f "/usr/local/lib/libndi.so.5" ]; then
    log_warn "NDI library not found. Make sure NDI SDK is installed"
fi

# Create service user if not exists
if ! id "$SERVICE_USER" &>/dev/null; then
    log_info "Creating service user: $SERVICE_USER"
    useradd -r -s /bin/false -d "$INSTALL_DIR" -m "$SERVICE_USER"
fi

# Add user to required groups
log_info "Adding $SERVICE_USER to video, audio, render groups..."
usermod -aG video "$SERVICE_USER" 2>/dev/null || true
usermod -aG audio "$SERVICE_USER" 2>/dev/null || true
usermod -aG render "$SERVICE_USER" 2>/dev/null || true

# Stop existing service if running
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log_info "Stopping existing service..."
    systemctl stop "$SERVICE_NAME"
fi

# Create installation directory structure
log_info "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/backend"
mkdir -p "$INSTALL_DIR/frontend"
mkdir -p "$INSTALL_DIR/configs/generated"

# Copy backend files
log_info "Installing backend..."
cp -r "$PROJECT_DIR/backend/"* "$INSTALL_DIR/backend/"

# Copy configs directory (preserve existing extra_ips.txt if present)
if [ -f "$INSTALL_DIR/configs/extra_ips.txt" ]; then
    log_info "Preserving existing extra_ips.txt"
    cp "$INSTALL_DIR/configs/extra_ips.txt" /tmp/extra_ips.txt.bak
fi

if [ -d "$PROJECT_DIR/configs" ]; then
    cp -r "$PROJECT_DIR/configs/"* "$INSTALL_DIR/configs/" 2>/dev/null || true
fi

if [ -f "/tmp/extra_ips.txt.bak" ]; then
    mv /tmp/extra_ips.txt.bak "$INSTALL_DIR/configs/extra_ips.txt"
fi

# Create extra_ips.txt if it doesn't exist
if [ ! -f "$INSTALL_DIR/configs/extra_ips.txt" ]; then
    log_info "Creating empty extra_ips.txt"
    touch "$INSTALL_DIR/configs/extra_ips.txt"
fi

# Install Python dependencies
log_info "Installing Python dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r "$INSTALL_DIR/backend/requirements.txt"
python3 -m pip install --quiet gunicorn

# Build frontend if npm is available
if command -v npm &>/dev/null; then
    log_info "Building frontend..."
    cd "$PROJECT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install --silent
    fi
    npm run build --silent

    # Copy frontend build
    log_info "Installing frontend..."
    rm -rf "$INSTALL_DIR/frontend/dist"
    cp -r "$PROJECT_DIR/frontend/dist" "$INSTALL_DIR/frontend/"
else
    log_warn "npm not found, skipping frontend build"
    log_warn "You'll need to build the frontend manually and copy to $INSTALL_DIR/frontend/dist"

    # Copy pre-built frontend if exists
    if [ -d "$PROJECT_DIR/frontend/dist" ]; then
        log_info "Copying pre-built frontend..."
        cp -r "$PROJECT_DIR/frontend/dist" "$INSTALL_DIR/frontend/"
    fi
fi

# Set permissions
log_info "Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# Create preview directory in ramdisk
log_info "Setting up preview directory..."
mkdir -p /dev/shm/extrashot_preview
chown "$SERVICE_USER:$SERVICE_USER" /dev/shm/extrashot_preview

# Install systemd service
log_info "Installing systemd service..."
cp "$SCRIPT_DIR/ndi-controller.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo ""
echo "=========================================="
echo "        Installation Complete!"
echo "=========================================="
echo ""
echo "Service commands:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "Web interface: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Configuration files:"
echo "  Extra IPs: $INSTALL_DIR/configs/extra_ips.txt"
echo "  Service:   /etc/systemd/system/$SERVICE_NAME.service"
echo ""
echo "To start the service now, run:"
echo "  sudo systemctl start $SERVICE_NAME"
echo ""
