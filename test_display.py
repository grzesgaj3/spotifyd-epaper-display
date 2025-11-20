#!/usr/bin/env python3
"""
Test script for Spotifyd E-Paper Display.
Simulates MPRIS metadata for testing without a real media player.
"""

import sys
import time
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from display_manager import DisplayManager
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_display():
    """Test the display with mock data."""
    print("=== Spotifyd E-Paper Display Test ===")
    print()
    
    # Load configuration
    config = Config()
    print(f"Display type: {config.display_type}")
    print(f"Display size: {config.display_width}x{config.display_height}")
    print()
    
    # Create display manager
    display_manager = DisplayManager(config)
    display_manager.initialize()
    
    # Test 1: Show idle screen
    print("Test 1: Showing idle screen...")
    display_manager.show_idle()
    time.sleep(2)
    
    # Test 2: Show playing track (beginning)
    print("Test 2: Showing playing track at start...")
    metadata = {
        'title': 'Bohemian Rhapsody',
        'artist': 'Queen',
        'album': 'A Night at the Opera',
        'status': 'Playing',
        'position': 0,  # 0 seconds in microseconds
        'length': 354000000,  # 5:54 in microseconds
        'art_url': '',
    }
    display_manager.update_display(metadata)
    time.sleep(2)
    
    # Test 3: Show playing track (middle)
    print("Test 3: Showing playing track at middle...")
    metadata['position'] = 120000000  # 2:00
    display_manager.update_display(metadata)
    time.sleep(2)
    
    # Test 4: Show paused track
    print("Test 4: Showing paused track...")
    metadata['status'] = 'Paused'
    metadata['position'] = 180000000  # 3:00
    display_manager.update_display(metadata)
    time.sleep(2)
    
    # Test 5: Show long title/artist (text wrapping)
    print("Test 5: Testing text wrapping with long names...")
    metadata = {
        'title': 'Supercalifragilisticexpialidocious - A Very Long Song Title That Should Wrap',
        'artist': 'The Beatles, John Lennon, Paul McCartney, George Harrison, Ringo Starr',
        'album': 'Abbey Road (Deluxe Anniversary Edition)',
        'status': 'Playing',
        'position': 45000000,  # 45 seconds
        'length': 210000000,  # 3:30
        'art_url': '',
    }
    display_manager.update_display(metadata)
    time.sleep(2)
    
    # Test 6: Simulate progress bar animation
    print("Test 6: Simulating progress bar animation...")
    metadata = {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'status': 'Playing',
        'position': 0,
        'length': 30000000,  # 30 seconds
        'art_url': '',
    }
    
    for i in range(11):
        metadata['position'] = int(i * 3000000)  # 3 seconds each step
        display_manager.update_display(metadata)
        print(f"  Progress: {i*10}%")
        time.sleep(0.5)
    
    # Cleanup
    print()
    print("Test complete!")
    print()
    
    if config.display_type == 'virtual':
        print("Output saved to: /tmp/display_output.png")
        print("You can view the image to see the final test result.")
    
    display_manager.cleanup()


def main():
    """Main test entry point."""
    try:
        test_display()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
