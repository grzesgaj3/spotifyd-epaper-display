#!/bin/bash
# Installation script for Spotifyd E-Paper Display

set -e

echo "=== Spotifyd E-Paper Display Installation ==="
echo ""

# Check if running on Linux
if [ "$(uname)" != "Linux" ]; then
    echo "Error: This script is designed for Linux systems (Raspberry Pi OS)"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="${INSTALL_DIR:-$HOME/spotifyd-epaper-display}"

echo "Installation directory: $INSTALL_DIR"
echo ""

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-pil python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
cd "$SCRIPT_DIR"
pip3 install --user -r requirements.txt

# Create config directory
echo ""
echo "Creating config directory..."
mkdir -p "$HOME/.config/spotifyd-display"

# Create example config if it doesn't exist
if [ ! -f "$HOME/.config/spotifyd-display/config.json" ]; then
    echo "Creating example configuration..."
    cat > "$HOME/.config/spotifyd-display/config.json" << EOF
{
  "display_type": "virtual",
  "display_width": 250,
  "display_height": 122,
  "epaper_model": "epd2in13_V2",
  "update_interval": 1.0,
  "log_level": "INFO"
}
EOF
    echo "Example config created at: $HOME/.config/spotifyd-display/config.json"
    echo "Edit this file to configure your display settings."
fi

# Copy files if not running from target directory
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    echo ""
    echo "Copying files to $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
fi

# Make main.py executable
chmod +x "$INSTALL_DIR/main.py"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To run the application manually:"
echo "  cd $INSTALL_DIR"
echo "  python3 main.py"
echo ""
echo "To install as a systemd service:"
echo "  sudo cp $INSTALL_DIR/spotifyd-display.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable spotifyd-display.service"
echo "  sudo systemctl start spotifyd-display.service"
echo ""
echo "Note: Edit the service file to match your installation path and user."
echo ""
echo "For e-paper display support, install waveshare-epd:"
echo "  pip3 install --user waveshare-epd"
echo ""
