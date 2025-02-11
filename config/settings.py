"""
Configuration manager for Lazzaran voice assistant.
Handles loading and managing all configuration settings.
"""

import os
import yaml
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class VoiceSettings:
    """Voice-related settings."""
    language: str
    timeout: int
    ambient_duration: int
    energy_threshold: int
    pause_threshold: float
    non_speaking_duration: float

@dataclass
class APIKeys:
    """API keys for various services."""
    weather_api_key: str
    news_api_key: str
    gemini_api_key: str

class ConfigManager:
    """Configuration manager class."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path(__file__).parent
        self.project_root = self.config_dir.parent
        self.temp_directory = self.project_root / "temp"
        
        # Create temp directory if it doesn't exist
        self.temp_directory.mkdir(exist_ok=True)
        
        # Load configurations
        self._load_config()
        self._load_system_paths()
        self._load_env_variables()
    
    def _load_config(self):
        """Load main configuration from YAML file."""
        config_file = self.config_dir / "config.yaml"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Parse voice settings
            voice_config = config.get('voice', {})
            self.voice_settings = VoiceSettings(
                language=voice_config.get('language', 'tr-TR'),
                timeout=voice_config.get('timeout', 5),
                ambient_duration=voice_config.get('ambient_duration', 1),
                energy_threshold=voice_config.get('energy_threshold', 4000),
                pause_threshold=voice_config.get('pause_threshold', 0.8),
                non_speaking_duration=voice_config.get('non_speaking_duration', 0.5)
            )
            
        except Exception as e:
            raise RuntimeError(f"Error loading config.yaml: {e}")
    
    def _load_system_paths(self):
        """Load system paths from JSON file."""
        paths_file = self.config_dir / "system_paths.json"
        try:
            with open(paths_file, 'r', encoding='utf-8') as f:
                self.system_paths = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading system_paths.json: {e}")
    
    def _load_env_variables(self):
        """Load API keys from environment variables."""
        self.api_keys = APIKeys(
            weather_api_key=os.getenv('WEATHER_API_KEY', ''),
            news_api_key=os.getenv('NEWS_API_KEY', ''),
            gemini_api_key=os.getenv('GEMINI_API_KEY', '')
        )
        
        # Validate API keys
        self._validate_api_keys()
    
    def _validate_api_keys(self):
        """Validate that all required API keys are present."""
        missing_keys = []
        for key, value in self.api_keys.__dict__.items():
            if not value:
                missing_keys.append(key)
        
        if missing_keys:
            raise RuntimeError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    def get_app_path(self, app_name: str) -> Optional[str]:
        """Get system path for a specific application."""
        return self.system_paths.get(app_name)
    
    def get_temp_file_path(self, filename: str) -> Path:
        """Get path for a temporary file."""
        return self.temp_directory / filename 