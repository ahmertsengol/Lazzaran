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

@dataclass
class VoiceAssistantConfig:
    language: str = 'tr-TR'
    timeout: int = 5
    ambient_duration: int = 1
    temp_audio_file: str = "response.mp3"
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    max_retries: int = 3
    retry_delay: float = 1.0

class VoiceAssistant:
    def __init__(self, config: Optional[VoiceAssistantConfig] = None):
        try:
            self.config = config or VoiceAssistantConfig()
            self.recognizer = sr.Recognizer()
            self.logger = logging.getLogger(__name__)
            
            # Initialize pygame mixer
            try:
                pygame.mixer.quit()  # Ensure clean state
                pygame.mixer.init(frequency=self.config.sample_rate)
            except Exception as e:
                self.logger.error(f"Error initializing audio system: {e}")
                raise
                
            # Adjust recognition parameters
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 4000
            self.recognizer.pause_threshold = 0.8
            self.recognizer.non_speaking_duration = 0.5
            
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise
        
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text."""
        retries = 0
        while retries < self.config.max_retries:
            try:
                # Record audio using sounddevice
                self.logger.info("Listening for speech...")
                recording = sd.rec(
                    int(self.config.sample_rate * self.config.timeout),
                    samplerate=self.config.sample_rate,
                    channels=self.config.channels,
                    dtype=np.int16,
                    blocking=True
                )
                
                # Convert recording to audio data
                audio_data = recording.tobytes()
                
                # Create an AudioData object
                audio = sr.AudioData(
                    audio_data,
                    sample_rate=self.config.sample_rate,
                    sample_width=2  # 16-bit audio
                )
                
                # Recognize speech
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.config.language,
                    show_all=False
                )
                
                if text:
                    self.logger.info(f"Recognized text: {text}")
                    return text.lower()  # Return lowercase for consistent command matching
                
            except sr.UnknownValueError:
                self.logger.info("Speech not understood")
                retries += 1
                if retries < self.config.max_retries:
                    time.sleep(self.config.retry_delay)
                
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
                break
                
            except Exception as e:
                self.logger.error(f"Error in speech recognition: {e}")
                break
        
        return None

    def speak(self, text: str) -> bool:
        """Convert text to speech and play it."""
        if not text:
            return False
            
        temp_file = None
        try:
            # Generate unique temporary file path
            temp_file = Path(self.config.temp_audio_file)
            
            # Generate speech
            tts = gTTS(text=text, lang=self.config.language.split('-')[0], slow=False)
            tts.save(str(temp_file))
            
            # Play audio
            pygame.mixer.music.load(str(temp_file))
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
            return False
            
        finally:
            self._cleanup_audio_file(temp_file)
    
    def _cleanup_audio_file(self, file_path: Optional[Path]):
        """Clean up temporary audio file."""
        if file_path and file_path.exists():
            try:
                pygame.mixer.music.unload()  # Ensure file is not in use
                file_path.unlink()
            except Exception as e:
                self.logger.error(f"Error cleaning up audio file: {e}")

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            pygame.mixer.quit()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}") 