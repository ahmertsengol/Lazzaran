"""
Core Voice Assistant module that handles speech recognition and command processing.
"""

import speech_recognition as sr
from gtts import gTTS
import os
import pygame
import logging
import sounddevice as sd
import numpy as np
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import time
import traceback
import threading
import queue

@dataclass
class VoiceAssistantConfig:
    """Configuration class for VoiceAssistant."""
    language: str = 'tr-TR'
    timeout: float = 5.0
    ambient_duration: float = 1.0
    temp_audio_file: str = "temp_response.mp3"
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    max_retries: int = 3
    retry_delay: float = 0.5
    energy_threshold: int = 4000
    pause_threshold: float = 0.8
    non_speaking_duration: float = 0.5
    dynamic_energy_threshold: bool = True

class VoiceAssistant:
    """Main voice assistant class that handles speech recognition and synthesis."""
    
    def __init__(self, config: Optional[VoiceAssistantConfig] = None):
        """Initialize the voice assistant with given or default configuration."""
        try:
            self.logger = logging.getLogger(__name__)
            self.logger.info("Initializing voice assistant...")
            
            self.config = config or VoiceAssistantConfig()
            self.logger.debug(f"Using configuration: {self.config}")
            
            self.recognizer = sr.Recognizer()
            self._is_listening = False
            self._is_speaking = False
            self._lock = threading.Lock()
            self._audio_queue = queue.Queue()
            
            # Initialize audio system
            self._init_audio_system()
            
            # Configure speech recognition
            self._configure_recognition()
            
            self.logger.info("Voice assistant initialized successfully")
            
        except Exception as e:
            self.logger.critical(f"Voice assistant initialization failed: {e}\n{traceback.format_exc()}")
            raise

    @property
    def is_listening(self):
        """Thread-safe access to listening state."""
        with self._lock:
            return self._is_listening

    @is_listening.setter
    def is_listening(self, value):
        """Thread-safe setting of listening state."""
        with self._lock:
            self._is_listening = value

    @property
    def is_speaking(self):
        """Thread-safe access to speaking state."""
        with self._lock:
            return self._is_speaking

    @is_speaking.setter
    def is_speaking(self, value):
        """Thread-safe setting of speaking state."""
        with self._lock:
            self._is_speaking = value
    
    def _init_audio_system(self):
        """Initialize the audio system for playback."""
        try:
            self.logger.debug("Initializing audio system...")
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=self.config.sample_rate)
            self.logger.debug("Audio system initialized successfully")
        except Exception as e:
            self.logger.error(f"Audio system initialization failed: {e}\n{traceback.format_exc()}")
            raise
    
    def _configure_recognition(self):
        """Configure speech recognition parameters."""
        try:
            self.logger.debug("Configuring speech recognition parameters...")
            self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            self.recognizer.energy_threshold = self.config.energy_threshold
            self.recognizer.pause_threshold = self.config.pause_threshold
            self.recognizer.non_speaking_duration = self.config.non_speaking_duration
            self.logger.debug("Speech recognition parameters configured successfully")
        except Exception as e:
            self.logger.error(f"Speech recognition configuration failed: {e}\n{traceback.format_exc()}")
            raise
    
    def start_listening(self):
        """Start the voice recognition."""
        self.logger.info("Starting voice recognition...")
        self.is_listening = True
        self.logger.debug("Voice recognition started successfully")
    
    def stop_listening(self):
        """Stop the voice recognition."""
        self.logger.info("Stopping voice recognition...")
        self.is_listening = False
        self.logger.debug("Voice recognition stopped successfully")
    
    def stop_speaking(self):
        """Stop the current speech output."""
        try:
            self.logger.info("Attempting to stop speech output...")
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                self.is_speaking = False
                self.logger.debug("Speech output stopped successfully")
            else:
                self.logger.debug("No active speech to stop")
        except Exception as e:
            self.logger.error(f"Error stopping speech output: {e}\n{traceback.format_exc()}")
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text."""
        if not self.is_listening:
            return None
            
        try:
            # Record audio using sounddevice
            self.logger.debug("Starting audio recording...")
            recording = sd.rec(
                int(self.config.sample_rate * self.config.timeout),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=np.int16,
                blocking=True
            )
            
            # Check if we're still listening after recording
            if not self.is_listening:
                self.logger.debug("Listening stopped during recording")
                return None
            
            # Convert recording to audio data
            self.logger.debug("Converting recording to audio data...")
            audio_data = recording.tobytes()
            
            # Create an AudioData object
            audio = sr.AudioData(
                audio_data,
                sample_rate=self.config.sample_rate,
                sample_width=2  # 16-bit audio
            )
            
            # Recognize speech
            self.logger.debug("Starting speech recognition...")
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.config.language,
                    show_all=False
                )
                
                if text and self.is_listening:
                    self.logger.info(f"Successfully recognized text: {text}")
                    return text.lower()
                    
            except sr.UnknownValueError:
                self.logger.debug("No speech detected")
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}\n{traceback.format_exc()}")
            
        return None

    def speak(self, text: str) -> bool:
        """Convert text to speech and play it."""
        if not text:
            self.logger.warning("Attempted to speak empty text")
            return False
            
        temp_file = None
        try:
            self.logger.info(f"Converting text to speech: {text}")
            self.is_speaking = True
            
            # Generate unique temporary file path
            temp_file = Path(self.config.temp_audio_file)
            self.logger.debug(f"Using temporary file: {temp_file}")
            
            # Ensure temp directory exists
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate speech
            self.logger.debug("Generating speech with gTTS...")
            tts = gTTS(text=text, lang=self.config.language.split('-')[0], slow=False)
            
            # Save with exclusive access
            with open(temp_file, 'wb') as f:
                tts.write_to_fp(f)
            self.logger.debug("Speech generated and saved successfully")
            
            # Play audio
            self.logger.debug("Loading audio file for playback...")
            pygame.mixer.music.load(str(temp_file))
            pygame.mixer.music.play()
            self.logger.debug("Audio playback started")
            
            # Wait for playback to finish or until stopped
            while pygame.mixer.music.get_busy() and self.is_speaking:
                pygame.time.Clock().tick(10)
            
            self.logger.debug("Audio playback completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}\n{traceback.format_exc()}")
            return False
            
        finally:
            self.is_speaking = False
            self._cleanup_audio_file(temp_file)
    
    def _cleanup_audio_file(self, file_path: Optional[Path]):
        """Clean up temporary audio file."""
        if file_path and file_path.exists():
            try:
                self.logger.debug(f"Cleaning up temporary file: {file_path}")
                pygame.mixer.music.unload()
                # Retry a few times if file is locked
                for _ in range(3):
                    try:
                        file_path.unlink()
                        break
                    except PermissionError:
                        time.sleep(0.1)
                self.logger.debug("Temporary file cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error cleaning up audio file: {e}\n{traceback.format_exc()}")

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.logger.debug("Cleaning up voice assistant resources...")
            pygame.mixer.quit()
            self.logger.debug("Voice assistant cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during voice assistant cleanup: {e}\n{traceback.format_exc()}") 