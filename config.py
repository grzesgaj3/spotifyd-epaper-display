#!/usr/bin/env python3
"""
Configuration management for Spotifyd E-Paper Display.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Config:
    """Configuration handler for the application."""
    
    DEFAULT_CONFIG = {
        'display_type': 'virtual',  # 'virtual', 'epaper', 'tft'
        'display_width': 250,
        'display_height': 122,
        'epaper_model': 'epd2in13_V2',  # For Waveshare e-paper displays
        'update_interval': 1.0,  # seconds
        'log_level': 'INFO',
    }
    
    def __init__(self, config_file: str = None):
        """Initialize configuration.
        
        Args:
            config_file: Path to JSON config file. If None, looks for:
                        1. Environment variable SPOTIFYD_DISPLAY_CONFIG
                        2. ~/.config/spotifyd-display/config.json
                        3. /etc/spotifyd-display/config.json
        """
        self.config_file = self._find_config_file(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        
        if self.config_file and Path(self.config_file).exists():
            self._load_config()
        else:
            logger.info("Using default configuration")
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _find_config_file(self, config_file: str = None) -> str:
        """Find configuration file."""
        if config_file:
            return config_file
        
        # Check environment variable
        env_config = os.environ.get('SPOTIFYD_DISPLAY_CONFIG')
        if env_config and Path(env_config).exists():
            return env_config
        
        # Check user config directory
        user_config = Path.home() / '.config' / 'spotifyd-display' / 'config.json'
        if user_config.exists():
            return str(user_config)
        
        # Check system config directory
        system_config = Path('/etc/spotifyd-display/config.json')
        if system_config.exists():
            return str(system_config)
        
        return None
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
                logger.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading config file {self.config_file}: {e}")
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        env_mapping = {
            'SPOTIFYD_DISPLAY_TYPE': 'display_type',
            'SPOTIFYD_DISPLAY_WIDTH': ('display_width', int),
            'SPOTIFYD_DISPLAY_HEIGHT': ('display_height', int),
            'SPOTIFYD_EPAPER_MODEL': 'epaper_model',
            'SPOTIFYD_UPDATE_INTERVAL': ('update_interval', float),
            'SPOTIFYD_LOG_LEVEL': 'log_level',
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                if isinstance(config_key, tuple):
                    config_key, converter = config_key
                    try:
                        value = converter(value)
                    except ValueError:
                        logger.warning(f"Invalid value for {env_var}: {value}")
                        continue
                
                self.config[config_key] = value
                logger.debug(f"Config override from env: {config_key} = {value}")
    
    def __getattr__(self, name: str) -> Any:
        """Allow accessing config values as attributes."""
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"Config has no attribute '{name}'")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def save_example_config(self, path: str = None):
        """Save an example configuration file."""
        if path is None:
            path = Path.home() / '.config' / 'spotifyd-display' / 'config.json'
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.DEFAULT_CONFIG, f, indent=2)
        
        logger.info(f"Example configuration saved to {path}")
