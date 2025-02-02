"""
Configuration management for the voice assistant application.
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dataclasses import dataclass

@dataclass
class APIConfig:
    gemini_api_key: str = None
    news_api_key: str = None
    weather_api_key: str = None

@dataclass
class VoiceConfig:
    language: str = 'tr-TR'
    timeout: int = 5
    ambient_duration: int = 1

@dataclass
class AppConfig:
    api: APIConfig
    voice: VoiceConfig
    temp_dir: Path

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration from environment variables and config file"""
        self.config_path = Path(__file__).parent / 'config.yaml'
        self.config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from YAML file and environment variables"""
        # Load from YAML
        config_data = {}
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        
        # Override with environment variables
        api_config = APIConfig(
            gemini_api_key=os.getenv('GEMINI_API_KEY', config_data.get('api', {}).get('gemini_api_key')),
            news_api_key=os.getenv('NEWS_API_KEY', config_data.get('api', {}).get('news_api_key')),
            weather_api_key=os.getenv('WEATHER_API_KEY', config_data.get('api', {}).get('weather_api_key'))
        )
        
        voice_config = VoiceConfig(
            language=os.getenv('VOICE_LANGUAGE', config_data.get('voice', {}).get('language', 'tr-TR')),
            timeout=int(os.getenv('VOICE_TIMEOUT', config_data.get('voice', {}).get('timeout', 5))),
            ambient_duration=int(os.getenv('AMBIENT_DURATION', config_data.get('voice', {}).get('ambient_duration', 1)))
        )
        
        temp_dir = Path(os.getenv('TEMP_DIR', config_data.get('temp_dir', Path.home() / '.lazzaran' / 'temp')))
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        return AppConfig(
            api=api_config,
            voice=voice_config,
            temp_dir=temp_dir
        )
    
    @property
    def api_keys(self) -> APIConfig:
        """Get API configuration"""
        return self.config.api
    
    @property
    def voice_settings(self) -> VoiceConfig:
        """Get voice configuration"""
        return self.config.voice
    
    @property
    def temp_directory(self) -> Path:
        """Get temporary directory path"""
        return self.config.temp_dir 