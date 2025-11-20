#!/usr/bin/env python3
"""
Spotifyd E-Paper Display
A Python application to display currently playing music on e-paper/TFT displays
for Raspberry Pi using MPRIS protocol.
"""

import sys
import time
import logging
import signal
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from pydbus import SessionBus
    from gi.repository import GLib
except ImportError as e:
    print(f"Error: Required dependencies not installed: {e}")
    print("Please install dependencies: pip3 install -r requirements.txt")
    sys.exit(1)

from display_manager import DisplayManager
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/spotifyd-display.log')
    ]
)
logger = logging.getLogger(__name__)


class MPRISClient:
    """Client for fetching music data via MPRIS protocol."""
    
    MPRIS_INTERFACE = "org.mpris.MediaPlayer2.Player"
    PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
    
    def __init__(self):
        self.bus = SessionBus()
        self.player_name = None
        self.player = None
        self.properties = None
        self._find_player()
    
    def _find_player(self):
        """Find an active MPRIS media player."""
        try:
            # Look for common music players
            player_names = [
                'org.mpris.MediaPlayer2.spotifyd',
                'org.mpris.MediaPlayer2.spotify',
                'org.mpris.MediaPlayer2.vlc',
                'org.mpris.MediaPlayer2.mpd',
                'org.mpris.MediaPlayer2.mopidy',
            ]
            
            for name in player_names:
                try:
                    self.player = self.bus.get(name, '/org/mpris/MediaPlayer2')
                    self.properties = self.player[self.PROPERTIES_INTERFACE]
                    self.player_name = name
                    logger.info(f"Connected to media player: {name}")
                    return
                except Exception:
                    continue
                    
            # If no specific player found, try to find any MPRIS player
            dbus_obj = self.bus.get('org.freedesktop.DBus', '/org/freedesktop/DBus')
            names = dbus_obj.ListNames()
            for name in names:
                if name.startswith('org.mpris.MediaPlayer2.'):
                    try:
                        self.player = self.bus.get(name, '/org/mpris/MediaPlayer2')
                        self.properties = self.player[self.PROPERTIES_INTERFACE]
                        self.player_name = name
                        logger.info(f"Connected to media player: {name}")
                        return
                    except Exception:
                        continue
                        
            logger.warning("No MPRIS media player found")
        except Exception as e:
            logger.error(f"Error finding media player: {e}")
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get current track metadata."""
        if not self.player or not self.properties:
            self._find_player()
            if not self.player:
                return None
        
        try:
            metadata = self.properties.Get(self.MPRIS_INTERFACE, 'Metadata')
            playback_status = self.properties.Get(self.MPRIS_INTERFACE, 'PlaybackStatus')
            position = self.properties.Get(self.MPRIS_INTERFACE, 'Position')
            
            if not metadata:
                return None
            
            # Extract common fields
            result = {
                'title': metadata.get('xesam:title', 'Unknown Title'),
                'artist': ', '.join(metadata.get('xesam:artist', ['Unknown Artist'])),
                'album': metadata.get('xesam:album', 'Unknown Album'),
                'length': metadata.get('mpris:length', 0),  # in microseconds
                'position': position,  # in microseconds
                'status': playback_status,  # Playing, Paused, or Stopped
                'art_url': metadata.get('mpris:artUrl', ''),
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            self.player = None
            return None


class SpotifydDisplay:
    """Main application class for the Spotifyd e-paper display."""
    
    def __init__(self, config: Config):
        self.config = config
        self.running = False
        self.mpris_client = MPRISClient()
        self.display_manager = DisplayManager(config)
        self.last_metadata = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the display update loop."""
        logger.info("Starting Spotifyd E-Paper Display")
        self.running = True
        
        try:
            self.display_manager.initialize()
            self._update_loop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application."""
        if self.running:
            logger.info("Stopping Spotifyd E-Paper Display")
            self.running = False
            self.display_manager.cleanup()
    
    def _update_loop(self):
        """Main update loop."""
        while self.running:
            try:
                # Get current metadata
                metadata = self.mpris_client.get_metadata()
                
                # Only update display if metadata changed or position updated significantly
                if self._should_update(metadata):
                    if metadata:
                        logger.debug(f"Updating display: {metadata.get('title')} - {metadata.get('artist')}")
                        self.display_manager.update_display(metadata)
                        self.last_metadata = metadata
                    else:
                        # No metadata available, show idle screen
                        if self.last_metadata is not None:
                            logger.info("No playback detected, showing idle screen")
                            self.display_manager.show_idle()
                            self.last_metadata = None
                
                # Sleep based on configuration
                time.sleep(self.config.update_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {e}", exc_info=True)
                time.sleep(5)  # Wait before retrying
    
    def _should_update(self, metadata: Optional[Dict[str, Any]]) -> bool:
        """Determine if display should be updated."""
        if metadata is None and self.last_metadata is None:
            return False  # No change, both are None
        
        if metadata is None or self.last_metadata is None:
            return True  # State changed
        
        # Check if track changed
        if (metadata.get('title') != self.last_metadata.get('title') or
            metadata.get('artist') != self.last_metadata.get('artist')):
            return True
        
        # Check if playback status changed
        if metadata.get('status') != self.last_metadata.get('status'):
            return True
        
        # Update progress bar periodically during playback
        if metadata.get('status') == 'Playing':
            return True
        
        return False


def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    
    # Create and start the application
    app = SpotifydDisplay(config)
    
    try:
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
