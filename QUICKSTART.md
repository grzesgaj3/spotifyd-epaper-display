# Quick Start Guide

This guide will help you get the Spotifyd E-Paper Display running quickly on your Raspberry Pi.

## Prerequisites

- Raspberry Pi (Zero W or any model) running Raspberry Pi OS
- E-paper or TFT display connected via GPIO
- Media player installed (Spotifyd, Spotify, MPD, etc.)

## Installation Steps

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/grzesgaj3/spotifyd-epaper-display.git
cd spotifyd-epaper-display
```

### 2. Run the Installation Script

```bash
./install.sh
```

This will:
- Install system dependencies
- Install Python packages
- Create configuration directory
- Set up example configuration

### 3. Configure Your Display

Edit the configuration file:

```bash
nano ~/.config/spotifyd-display/config.json
```

For **e-paper displays** (Waveshare 2.13" v2):
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

For **testing without hardware**:
```json
{
  "display_type": "virtual",
  "display_width": 250,
  "display_height": 122,
  "update_interval": 1.0,
  "log_level": "INFO"
}
```

### 4. Enable SPI (for e-paper displays)

```bash
sudo raspi-config
```

Navigate to: `Interface Options → SPI → Enable`

Reboot after enabling SPI:
```bash
sudo reboot
```

### 5. Install E-Paper Library (if using e-paper)

```bash
pip3 install --user waveshare-epd
```

### 6. Test the Application

Run the test script to verify everything works:

```bash
python3 test_display.py
```

If using virtual display, check the output:
```bash
display /tmp/display_output.png  # or use your image viewer
```

### 7. Run the Application

Start manually:
```bash
python3 main.py
```

Or install as a service (see below).

## Setting Up as a Systemd Service

### 1. Edit the Service File

Update paths in `spotifyd-display.service` to match your installation:

```bash
nano spotifyd-display.service
```

Change:
- `User=pi` to your username
- `Group=pi` to your group
- `/home/pi/spotifyd-epaper-display` to your installation path
- Update `DBUS_SESSION_BUS_ADDRESS` if needed (check with `echo $DBUS_SESSION_BUS_ADDRESS`)

### 2. Install the Service

```bash
sudo cp spotifyd-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable spotifyd-display.service
```

### 3. Start the Service

```bash
sudo systemctl start spotifyd-display.service
```

### 4. Check Status

```bash
sudo systemctl status spotifyd-display.service
```

### 5. View Logs

```bash
# Follow live logs
sudo journalctl -u spotifyd-display.service -f

# View recent logs
sudo journalctl -u spotifyd-display.service -n 100
```

## Using with Spotifyd

### Install Spotifyd

```bash
sudo apt-get install spotifyd
```

### Configure Spotifyd

Create `~/.config/spotifyd/spotifyd.conf`:

```ini
[global]
username = "YOUR_SPOTIFY_USERNAME"
password = "YOUR_SPOTIFY_PASSWORD"
backend = "alsa"
device_name = "Raspberry Pi"
bitrate = 320
cache_path = "/home/pi/.cache/spotifyd"
volume_normalisation = true
normalisation_pregain = -10
```

### Start Spotifyd

```bash
spotifyd --no-daemon
```

Or as a service:
```bash
sudo systemctl enable spotifyd
sudo systemctl start spotifyd
```

## Troubleshooting

### Display Not Working

**Check if SPI is enabled:**
```bash
lsmod | grep spi
# Should show: spi_bcm2835
```

**Check GPIO permissions:**
```bash
sudo usermod -a -G gpio,spi $USER
```
Log out and back in for changes to take effect.

### No Media Player Found

**List MPRIS players:**
```bash
dbus-send --session --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep mpris
```

**Check D-Bus session address:**
```bash
echo $DBUS_SESSION_BUS_ADDRESS
```

If running as a service, make sure the `DBUS_SESSION_BUS_ADDRESS` in the service file matches.

### Service Fails to Start

**Check logs:**
```bash
sudo journalctl -u spotifyd-display.service -n 50
```

**Test manually first:**
```bash
cd ~/spotifyd-epaper-display
python3 main.py
```

## Next Steps

- Customize the display layout in `display_manager.py`
- Add album art display (requires additional implementation)
- Set up auto-start on boot
- Configure your favorite music player

## Support

For issues and questions:
- Check the main [README.md](README.md)
- Open an issue on GitHub
- Review logs for error messages
