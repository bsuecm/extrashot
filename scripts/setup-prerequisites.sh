#!/bin/bash
# Extrashot Prerequisites Setup Script
# Installs NDI SDK and libyuri (yuri2) for Raspberry Pi
#
# This script must be run before install.sh on a fresh system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo ""
echo "=========================================="
echo "   Extrashot Prerequisites Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (sudo ./setup-prerequisites.sh)"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
case "$ARCH" in
    aarch64)
        LIB_ARCH="aarch64-rpi4-linux-gnueabi"
        ;;
    armv7l)
        LIB_ARCH="arm-rpi4-linux-gnueabihf"
        ;;
    x86_64)
        LIB_ARCH="x86_64-linux-gnu"
        ;;
    *)
        log_error "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

log_info "Detected architecture: $ARCH ($LIB_ARCH)"

#################################################################
# Step 1: Install system dependencies
#################################################################
log_step "Installing system dependencies..."

apt-get update
apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    libsdl2-dev \
    libboost-all-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    python3 \
    python3-venv \
    python3-pip \
    curl \
    x11-xserver-utils

# Install Node.js if not present (for frontend build)
if ! command -v node &>/dev/null; then
    log_info "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
else
    log_info "Node.js already installed: $(node --version)"
fi

log_info "System dependencies installed."

#################################################################
# Step 2: Install NDI SDK
#################################################################
log_step "Installing NDI SDK v6..."

if [ -f "/usr/local/lib/libndi.so.6" ]; then
    log_info "NDI SDK already installed."
else
    LIBNDI_INSTALLER_NAME="Install_NDI_SDK_v6_Linux"
    LIBNDI_INSTALLER="$LIBNDI_INSTALLER_NAME.tar.gz"
    LIBNDI_INSTALLER_URL="https://downloads.ndi.tv/SDK/NDI_SDK_Linux/$LIBNDI_INSTALLER"

    LIBNDI_TMP=$(mktemp -d /tmp/ndisdk.XXXXXXX)

    log_info "Downloading NDI SDK..."
    curl -L "$LIBNDI_INSTALLER_URL" -f --retry 5 -o "$LIBNDI_TMP/$LIBNDI_INSTALLER"

    log_info "Extracting NDI SDK..."
    tar -xzf "$LIBNDI_TMP/$LIBNDI_INSTALLER" -C "$LIBNDI_TMP"

    # Run the NDI installer script (accepts license automatically)
    pushd "$LIBNDI_TMP" > /dev/null
    yes | PAGER="cat" sh "$LIBNDI_INSTALLER_NAME.sh"
    popd > /dev/null

    # Rename folder to avoid spaces
    mv "$LIBNDI_TMP/NDI SDK for Linux" "$LIBNDI_TMP/ndisdk"

    # Verify library exists for our architecture
    if [ ! -d "$LIBNDI_TMP/ndisdk/lib/$LIB_ARCH" ]; then
        log_error "NDI library not found for architecture: $LIB_ARCH"
        log_error "Available architectures:"
        ls -la "$LIBNDI_TMP/ndisdk/lib/"
        exit 1
    fi

    # Install libraries and headers
    log_info "Installing NDI libraries..."
    mkdir -p /usr/local/lib
    mkdir -p /usr/local/include
    mkdir -p /usr/share/ndi

    cp -P "$LIBNDI_TMP/ndisdk/lib/$LIB_ARCH/"* /usr/local/lib/
    cp -r "$LIBNDI_TMP/ndisdk/include/"* /usr/local/include/

    # Create backward compatibility symlink
    if [ ! -f /usr/local/lib/libndi.so.5 ]; then
        ln -sf /usr/local/lib/libndi.so.6 /usr/local/lib/libndi.so.5
    fi

    ldconfig

    # Cleanup
    rm -rf "$LIBNDI_TMP"

    log_info "NDI SDK installed."
fi

# Verify NDI installation
if [ -f "/usr/local/lib/libndi.so.6" ]; then
    log_info "NDI library verified: $(ls -la /usr/local/lib/libndi.so.6)"
else
    log_error "NDI library installation failed!"
    exit 1
fi

#################################################################
# Step 3: Build and install libyuri (yuri2)
#################################################################
log_step "Building and installing yuri2..."

if command -v yuri2 &>/dev/null; then
    log_info "yuri2 already installed: $(which yuri2)"
    YURI_INSTALLED=true
else
    YURI_INSTALLED=false
fi

if [ "$YURI_INSTALLED" = false ] || [ "$1" = "--force-yuri" ]; then
    YURI_TMP=$(mktemp -d /tmp/libyuri.XXXXXXX)

    log_info "Cloning libyuri..."
    git clone --depth 1 https://github.com/bsuecm/libyuri.git "$YURI_TMP/libyuri"

    # Remove modules incompatible with ffmpeg 7 (not needed for NDI functionality)
    log_info "Removing incompatible modules..."
    rm -rf "$YURI_TMP/libyuri/src/modules/rawavfile"
    rm -rf "$YURI_TMP/libyuri/src/modules/avdemux"
    rm -rf "$YURI_TMP/libyuri/src/modules/ultragrid"

    # Also remove references from CMakeLists.txt
    MODULES_CMAKE="$YURI_TMP/libyuri/src/modules/CMakeLists.txt"
    if [ -f "$MODULES_CMAKE" ]; then
        sed -i '/add_subdirectory.*rawavfile/d' "$MODULES_CMAKE"
        sed -i '/add_subdirectory.*avdemux/d' "$MODULES_CMAKE"
        sed -i '/add_subdirectory.*ultragrid/d' "$MODULES_CMAKE"
    fi

    log_info "Configuring build..."
    mkdir -p "$YURI_TMP/libyuri/build"
    cd "$YURI_TMP/libyuri/build"

    # Configure with NDI support
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DNDI_INCLUDE_DIRS=/usr/local/include \
        -DNDI_LIBRARIES=/usr/local/lib/libndi.so.6

    log_info "Building yuri2 (this may take a while on Raspberry Pi)..."
    make -j$(nproc)

    log_info "Installing yuri2..."
    make install
    ldconfig

    # Cleanup
    rm -rf "$YURI_TMP"

    log_info "yuri2 installed."
fi

# Verify yuri2 installation
if command -v yuri2 &>/dev/null; then
    log_info "yuri2 verified: $(which yuri2)"
else
    # Check if it's in /usr/local/bin
    if [ -f "/usr/local/bin/yuri2" ]; then
        log_info "yuri2 installed at /usr/local/bin/yuri2"
    else
        log_error "yuri2 installation failed!"
        exit 1
    fi
fi

#################################################################
# Complete
#################################################################
echo ""
echo "=========================================="
echo "   Prerequisites Installation Complete!"
echo "=========================================="
echo ""
echo "Installed components:"
echo "  - System build dependencies"
echo "  - SDL2 development libraries"
echo "  - NDI SDK v6"
echo "  - yuri2 media framework"
echo "  - Node.js (for frontend build)"
echo ""
echo "You can now install Extrashot:"
echo "  sudo ./scripts/install.sh"
echo ""
