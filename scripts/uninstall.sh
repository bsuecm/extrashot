#!/bin/bash
# NDI Controller Uninstall Script

set -e

INSTALL_DIR="/opt/ndi-controller"
SERVICE_USER="ndi"
SERVICE_NAME="ndi-controller"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo ""
echo "=========================================="
echo "   NDI Controller Uninstaller"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Please run as root (sudo ./uninstall.sh)"
    exit 1
fi

# Confirm uninstall
read -p "This will remove NDI Controller. Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

# Stop and disable service
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log_info "Stopping service..."
    systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    log_info "Disabling service..."
    systemctl disable "$SERVICE_NAME"
fi

# Remove service file
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    log_info "Removing systemd service..."
    rm -f "/etc/systemd/system/$SERVICE_NAME.service"
    systemctl daemon-reload
fi

# Ask about removing installation directory
if [ -d "$INSTALL_DIR" ]; then
    read -p "Remove installation directory ($INSTALL_DIR)? This will delete configs! [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Removing installation directory..."
        rm -rf "$INSTALL_DIR"
    else
        log_warn "Installation directory preserved at $INSTALL_DIR"
    fi
fi

# Clean up preview directory
if [ -d "/dev/shm/extrashot_preview" ]; then
    log_info "Cleaning up preview directory..."
    rm -rf "/dev/shm/extrashot_preview"
fi

# Ask about removing user
if id "$SERVICE_USER" &>/dev/null; then
    read -p "Remove service user ($SERVICE_USER)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Removing service user..."
        userdel "$SERVICE_USER" 2>/dev/null || true
    fi
fi

echo ""
echo "=========================================="
echo "        Uninstall Complete!"
echo "=========================================="
echo ""
