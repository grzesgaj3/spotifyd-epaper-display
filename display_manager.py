#!/usr/bin/env python3
"""
Display Manager - Handles rendering content to various display types.
Supports e-paper displays, TFT displays, and virtual displays for testing.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"Error: PIL/Pillow not installed: {e}")
    print("Please install: pip3 install Pillow")
    raise

from config import Config

logger = logging.getLogger(__name__)


class DisplayDriver:
    """Base class for display drivers."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def init(self):
        """Initialize the display hardware."""
        pass
    
    def display(self, image: Image.Image):
        """Display an image on the hardware."""
        raise NotImplementedError
    
    def sleep(self):
        """Put display into sleep mode."""
        pass
    
    def clear(self):
        """Clear the display."""
        pass


class VirtualDisplayDriver(DisplayDriver):
    """Virtual display driver for testing without hardware."""
    
    def __init__(self, width: int, height: int, output_dir: str = "/tmp"):
        super().__init__(width, height)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Virtual display initialized: {width}x{height}")
    
    def init(self):
        logger.info("Virtual display ready")
    
    def display(self, image: Image.Image):
        """Save image to file for testing."""
        output_path = self.output_dir / "display_output.png"
        image.save(output_path)
        logger.debug(f"Display output saved to {output_path}")


class EPaperDisplayDriver(DisplayDriver):
    """E-paper display driver (Waveshare compatible)."""
    
    # Mapping of model names to their import modules
    EPAPER_MODELS = {
        'epd2in13_V2': 'epd2in13_V2',
        'epd2in13_V3': 'epd2in13_V3',
        'epd2in7': 'epd2in7',
        'epd2in9': 'epd2in9',
        'epd4in2': 'epd4in2',
        'epd7in5': 'epd7in5',
    }
    
    def __init__(self, width: int, height: int, model: str = "epd2in13_V2"):
        super().__init__(width, height)
        self.model = model
        self.epd = None
        
        try:
            # Try to import waveshare e-paper library
            if model in self.EPAPER_MODELS:
                module_name = self.EPAPER_MODELS[model]
                module = __import__(f'waveshare_epd.{module_name}', fromlist=[module_name])
                epd_class = getattr(module, 'EPD')
                self.epd = epd_class()
            else:
                logger.warning(f"Unknown e-paper model: {model}, using virtual display")
        except ImportError:
            logger.warning("Waveshare e-paper library not found, using virtual display")
            self.epd = None
        except Exception as e:
            logger.warning(f"Error initializing e-paper display: {e}, using virtual display")
            self.epd = None
    
    def init(self):
        if self.epd:
            logger.info(f"Initializing e-paper display: {self.model}")
            self.epd.init()
            self.epd.Clear(0xFF)
        else:
            logger.info("E-paper hardware not available, using virtual display")
    
    def display(self, image: Image.Image):
        if self.epd:
            # Convert to 1-bit image for e-paper
            image_bw = image.convert('1')
            self.epd.display(self.epd.getbuffer(image_bw))
        else:
            # Fallback to virtual display
            output_path = Path("/tmp/display_output.png")
            image.save(output_path)
            logger.debug(f"Display output saved to {output_path}")
    
    def sleep(self):
        if self.epd:
            self.epd.sleep()
    
    def clear(self):
        if self.epd:
            self.epd.Clear(0xFF)


class DisplayManager:
    """Manages display rendering and updates."""
    
    def __init__(self, config: Config):
        self.config = config
        self.driver = self._create_driver()
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self._load_fonts()
    
    def _create_driver(self) -> DisplayDriver:
        """Create appropriate display driver based on configuration."""
        display_type = self.config.display_type
        width = self.config.display_width
        height = self.config.display_height
        
        if display_type == "epaper":
            return EPaperDisplayDriver(width, height, self.config.epaper_model)
        elif display_type == "virtual":
            return VirtualDisplayDriver(width, height)
        else:
            logger.warning(f"Unknown display type: {display_type}, using virtual")
            return VirtualDisplayDriver(width, height)
    
    def _load_fonts(self):
        """Load fonts for rendering text."""
        try:
            # Try to load DejaVu fonts (common on Linux)
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except Exception:
            try:
                # Try alternative font paths
                self.font_large = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 20)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 16)
                self.font_small = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 12)
            except Exception:
                # Fallback to default font
                logger.warning("Could not load TrueType fonts, using default font")
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
    
    def initialize(self):
        """Initialize the display hardware."""
        logger.info("Initializing display manager")
        self.driver.init()
    
    def cleanup(self):
        """Cleanup display resources."""
        logger.info("Cleaning up display manager")
        self.driver.sleep()
    
    def update_display(self, metadata: Dict[str, Any]):
        """Update display with current track information."""
        # Create image
        image = Image.new('RGB' if self.config.display_type != 'epaper' else 'L',
                         (self.driver.width, self.driver.height),
                         color='white')
        draw = ImageDraw.Draw(image)
        
        # Extract metadata
        title = metadata.get('title', 'Unknown Title')
        artist = metadata.get('artist', 'Unknown Artist')
        album = metadata.get('album', 'Unknown Album')
        status = metadata.get('status', 'Stopped')
        position = metadata.get('position', 0) // 1000000  # Convert to seconds
        length = metadata.get('length', 0) // 1000000  # Convert to seconds
        
        # Layout parameters
        margin = 5
        y_pos = margin
        
        # Draw status icon
        status_icon = "▶" if status == "Playing" else "⏸" if status == "Paused" else "⏹"
        draw.text((margin, y_pos), status_icon, fill='black', font=self.font_medium)
        y_pos += 25
        
        # Draw title (bold, larger)
        title_wrapped = self._wrap_text(title, self.font_large, self.driver.width - 2 * margin)
        for line in title_wrapped[:2]:  # Max 2 lines for title
            draw.text((margin, y_pos), line, fill='black', font=self.font_large)
            y_pos += 25
        
        # Draw artist
        artist_wrapped = self._wrap_text(artist, self.font_medium, self.driver.width - 2 * margin)
        for line in artist_wrapped[:1]:  # Max 1 line for artist
            draw.text((margin, y_pos), line, fill='black', font=self.font_medium)
            y_pos += 20
        
        # Draw album
        album_wrapped = self._wrap_text(album, self.font_small, self.driver.width - 2 * margin)
        for line in album_wrapped[:1]:  # Max 1 line for album
            draw.text((margin, y_pos), line, fill='black', font=self.font_small)
            y_pos += 18
        
        # Draw progress bar
        if length > 0:
            y_pos = self.driver.height - 35
            progress = position / length if length > 0 else 0
            progress = min(1.0, max(0.0, progress))
            
            # Progress bar dimensions
            bar_width = self.driver.width - 2 * margin
            bar_height = 10
            bar_x = margin
            bar_y = y_pos
            
            # Draw progress bar background
            draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                          outline='black', fill='white')
            
            # Draw progress bar fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                draw.rectangle([bar_x, bar_y, bar_x + fill_width, bar_y + bar_height],
                              fill='black')
            
            # Draw time labels
            time_text = f"{self._format_time(position)} / {self._format_time(length)}"
            draw.text((margin, bar_y + bar_height + 2), time_text, fill='black', font=self.font_small)
        
        # Send to display
        self.driver.display(image)
    
    def show_idle(self):
        """Show idle screen when no music is playing."""
        image = Image.new('RGB' if self.config.display_type != 'epaper' else 'L',
                         (self.driver.width, self.driver.height),
                         color='white')
        draw = ImageDraw.Draw(image)
        
        # Center text
        text = "No music playing"
        bbox = draw.textbbox((0, 0), text, font=self.font_medium)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.driver.width - text_width) // 2
        y = (self.driver.height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=self.font_medium)
        
        self.driver.display(image)
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        if not text:
            return [""]
        
        words = text.split()
        lines = []
        current_line = []
        
        # Create a single temporary draw object for all measurements
        temp_image = Image.new('L', (1, 1))
        temp_draw = ImageDraw.Draw(temp_image)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [""]
    
    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
