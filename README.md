# Spotifyd E-Paper Display

A Python application that displays currently playing music information on e-paper or TFT displays connected to a Raspberry Pi. Retrieves playback data via MPRIS protocol from Spotifyd, Spotify, or other compatible media players.

## Features

- 🎵 **Real-time playback display** - Shows currently playing song information
- 📊 **Progress bar** - Visual progress indicator with time elapsed/remaining
- 🖥️ **Multiple display types** - Support for e-paper, TFT, and virtual displays
- 🔌 **MPRIS protocol** - Compatible with Spotifyd, Spotify, MPD, Mopidy, VLC, and more
- ⚙️ **Systemd integration** - Run as a background service
- 🎛️ **Configurable** - JSON config file or environment variables
- 📝 **Logging** - Comprehensive logging for debugging

## Hardware Requirements

- **Raspberry Pi Zero W** (or any Raspberry Pi model)
- **DAC HAT** (optional, for audio output)
- **E-paper display** (e.g., Waveshare 2.13" e-paper) or TFT display
- **GPIO connection** to display

### Tested Displays

- Waveshare 2.13" e-paper (250x122)
- Waveshare 2.7" e-paper (264x176)
- Other SPI-based displays (with appropriate drivers)

## Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- Media player with MPRIS support (Spotifyd, Spotify, MPD, etc.)

## Installation

### Quick Install

Run the installation script:

```bash
git clone https://github.com/grzesgaj3/spotifyd-epaper-display.git
cd spotifyd-epaper-display
./install.sh
```

### Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/grzesgaj3/spotifyd-epaper-display.git
   cd spotifyd-epaper-display
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip python3-pil python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```

3. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **For e-paper displays, install Waveshare library:**
   ```bash
   pip3 install waveshare-epd
   ```

5. **Enable SPI interface (for e-paper displays):**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options -> SPI -> Enable
   ```

## Configuration

Create a config file at `~/.config/spotifyd-display/config.json`:

```json
{
  "display_type": "epaper",
  "display_width": 250,
  "display_height": 122,
  "epaper_model": "epd2in13_V2",
  "update_interval": 1.0,
  "log_level": "INFO"
}
```

### Configuration Options

| Option | Description | Default | Values |
|--------|-------------|---------|--------|
| `display_type` | Type of display | `virtual` | `virtual`, `epaper`, `tft` |
| `display_width` | Display width in pixels | `250` | Integer |
| `display_height` | Display height in pixels | `122` | Integer |
| `epaper_model` | Waveshare e-paper model | `epd2in13_V2` | `epd2in13_V2`, `epd2in7`, etc. |
| `update_interval` | Update frequency in seconds | `1.0` | Float |
| `log_level` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Environment Variables

You can override configuration with environment variables:

- `SPOTIFYD_DISPLAY_TYPE` - Display type
- `SPOTIFYD_DISPLAY_WIDTH` - Display width
- `SPOTIFYD_DISPLAY_HEIGHT` - Display height
- `SPOTIFYD_EPAPER_MODEL` - E-paper model
- `SPOTIFYD_UPDATE_INTERVAL` - Update interval
- `SPOTIFYD_LOG_LEVEL` - Log level
- `SPOTIFYD_DISPLAY_CONFIG` - Path to config file

## Usage

### Run Manually

```bash
python3 main.py
```

For testing without hardware, the app will use a virtual display and save output to `/tmp/display_output.png`.

### Run as Systemd Service

1. **Edit the service file** to match your installation:
   ```bash
   nano spotifyd-display.service
   # Update paths and user as needed
   ```

2. **Install the service:**
   ```bash
   sudo cp spotifyd-display.service /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl enable spotifyd-display.service
   sudo systemctl start spotifyd-display.service
   ```

4. **Check status:**
   ```bash
   sudo systemctl status spotifyd-display.service
   ```

5. **View logs:**
   ```bash
   sudo journalctl -u spotifyd-display.service -f
   ```

## Display Layout

The display shows:

```
▶ [Playing/Paused status]
Title of the Song
Artist Name
Album Name

[=========>        ] Progress Bar
00:45 / 03:30      Time
```

## MPRIS Compatible Players

This application works with any MPRIS-compliant media player:

- **Spotifyd** - Lightweight Spotify client
- **Spotify** - Official Spotify desktop client
- **MPD** - Music Player Daemon
- **Mopidy** - Extensible music server
- **VLC** - Media player
- **Rhythmbox** - GNOME music player
- And many more...

## Troubleshooting

### No media player found

**Problem:** Application logs "No MPRIS media player found"

**Solution:**
- Ensure your media player is running
- Check if the player supports MPRIS: `dbus-send --session --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep mpris`
- Make sure the session D-Bus is accessible

### E-paper display not working

**Problem:** Display shows "Waveshare e-paper library not found"

**Solution:**
- Install waveshare-epd: `pip3 install waveshare-epd`
- Enable SPI interface: `sudo raspi-config`
- Check GPIO connections

### Display not updating

**Problem:** Display shows old information

**Solution:**
- Check logs: `tail -f /tmp/spotifyd-display.log`
- Verify media player is actually playing
- Increase `update_interval` if needed

### Permission errors

**Problem:** "Permission denied" errors accessing GPIO

**Solution:**
- Add user to `gpio` and `spi` groups:
  ```bash
  sudo usermod -a -G gpio,spi $USER
  ```
- Reboot or re-login

## Development

### Project Structure

```
spotifyd-epaper-display/
├── main.py              # Main application entry point
├── display_manager.py   # Display rendering and driver abstraction
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── install.sh         # Installation script
├── spotifyd-display.service  # Systemd service file
└── README.md          # This file
```

### Adding New Display Drivers

To add support for a new display type, create a new driver class in `display_manager.py` that inherits from `DisplayDriver`:

```python
class MyDisplayDriver(DisplayDriver):
    def init(self):
        # Initialize your display
        pass
    
    def display(self, image: Image.Image):
        # Send image to display
        pass
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

- MPRIS specification for media player control
- Waveshare for e-paper display libraries
- Spotifyd project for lightweight Spotify playback