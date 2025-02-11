"""
Main entry point for the Lazzaran Voice Assistant application.
"""

import logging
import sys
import asyncio
import threading
from pathlib import Path
import traceback
from concurrent.futures import ThreadPoolExecutor
from core.voice_assistant import VoiceAssistant, VoiceAssistantConfig
from core.command_handler import CommandHandler
from core.services.weather import WeatherService
from core.services.news import NewsService
from core.services.ai_service import AIService
from core.services.system_service import SystemService
from ui.display import VoiceAssistantUI
from config.settings import ConfigManager
from dotenv import load_dotenv
import os

# Setup logging with detailed configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('lazzaran_detailed.log', encoding='utf-8', mode='w'),
    ]
)

# Add error-specific file handler
error_handler = logging.FileHandler('lazzaran_errors.log', encoding='utf-8', mode='w')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'))
logging.getLogger().addHandler(error_handler)

logger = logging.getLogger(__name__)

class LazzaranApp:
    def __init__(self):
        try:
            logger.info("Initializing Lazzaran Voice Assistant...")
            
            # Load environment variables
            load_dotenv()
            logger.debug("Environment variables loaded")
            
            # Initialize configuration
            self.config = ConfigManager()
            logger.debug("Configuration manager initialized")
            
            # Initialize components
            self.setup_components()
            
            # Initialize thread pool
            self.executor = ThreadPoolExecutor(max_workers=3)
            logger.debug("Thread pool executor initialized")
            
            # Initialize state variables
            self.running = True
            self.listen_thread = None
            
            logger.info("Lazzaran Voice Assistant initialized successfully")
            
        except Exception as e:
            logger.critical(f"Fatal error during initialization: {e}\n{traceback.format_exc()}")
            raise
        
    def setup_components(self):
        """Initialize all application components"""
        try:
            logger.info("Setting up application components...")
            
            # Initialize voice assistant
            voice_config = VoiceAssistantConfig(
                language=self.config.voice_settings.language,
                timeout=self.config.voice_settings.timeout,
                ambient_duration=self.config.voice_settings.ambient_duration,
                temp_audio_file=str(self.config.temp_directory / "response.mp3")
            )
            self.voice_assistant = VoiceAssistant(config=voice_config)
            logger.debug("Voice assistant initialized")
            
            # Initialize services
            self.weather_service = WeatherService(
                api_key=self.config.api_keys.weather_api_key,
                language=self.config.voice_settings.language.split('-')[0]
            )
            logger.debug("Weather service initialized")
            
            self.news_service = NewsService(
                api_key=self.config.api_keys.news_api_key,
                language=self.config.voice_settings.language.split('-')[0]
            )
            logger.debug("News service initialized")
            
            self.ai_service = AIService(
                api_key=self.config.api_keys.gemini_api_key
            )
            logger.debug("AI service initialized")
            
            self.system_service = SystemService(voice_assistant=self.voice_assistant)
            logger.debug("System service initialized")
            
            # Initialize command handler with services
            self.command_handler = CommandHandler(
                weather_service=self.weather_service,
                news_service=self.news_service,
                ai_service=self.ai_service,
                system_service=self.system_service
            )
            logger.debug("Command handler initialized")
            
            # Initialize UI with system service
            self.ui = VoiceAssistantUI(
                system_service=self.system_service,
                on_start=self.start_listening,
                on_stop=self.stop_listening
            )
            logger.debug("UI initialized")
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.critical(f"Component initialization failed: {e}\n{traceback.format_exc()}")
            raise
        
    async def process_voice_command(self, text: str):
        """Process voice command asynchronously"""
        if not text:
            return
            
        try:
            logger.info(f"Processing voice command: {text}")
            response = await self.command_handler.process_command(text)
            
            if response:
                logger.debug(f"Command response: {response}")
                self.ui.log_message(f"Lazzaran: {response}", "success")
                await self.speak_response(response)
                
                # Refresh application list
                self.ui.refresh_app_list()
                logger.debug("Application list refreshed")
                
        except Exception as e:
            error_msg = f"Komut işlenirken hata oluştu: {str(e)}"
            logger.error(f"Command processing error: {e}\n{traceback.format_exc()}")
            self.ui.log_message(error_msg, "error")
            await self.speak_response("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.")
    
    async def speak_response(self, text: str):
        """Speak the response asynchronously"""
        try:
            logger.debug(f"Speaking response: {text}")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self.voice_assistant.speak, text)
            logger.debug("Response spoken successfully")
        except Exception as e:
            logger.error(f"Speech output error: {e}\n{traceback.format_exc()}")
            self.ui.log_message("Ses çıkışı sırasında bir hata oluştu", "error")
    
    async def listen_loop(self):
        """Main listening loop"""
        logger.debug("Starting listen loop")
        while self.running and self.ui.is_listening:
            try:
                # Check if we should be listening
                if not self.ui.is_listening:
                    logger.debug("Listening is disabled, waiting...")
                    await asyncio.sleep(0.1)
                    continue

                # Try to get voice input
                text = self.voice_assistant.listen()
                if text:
                    self.ui.log_message(f"Siz: {text}", "info")
                    await self.process_voice_command(text)
                else:
                    await asyncio.sleep(0.1)  # Prevent busy waiting
                    
            except Exception as e:
                logger.error(f"Voice recognition error: {e}\n{traceback.format_exc()}")
                self.ui.log_message("Ses tanıma sırasında bir hata oluştu. Yeniden başlatılıyor...", "error")
                await asyncio.sleep(1)  # Prevent rapid retries

        logger.debug("Listen loop ended")

    def run_async_loop(self):
        """Run the async event loop in a separate thread"""
        try:
            logger.debug("Starting async event loop")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the listen loop
            loop.run_until_complete(self.listen_loop())
            loop.close()
            logger.debug("Async event loop closed")
            
        except Exception as e:
            logger.error(f"Error in async loop: {e}\n{traceback.format_exc()}")
    
    def start_listening(self):
        """Start the voice recognition loop in a separate thread"""
        try:
            logger.info("Starting voice recognition")
            self.ui.log_message("Ses tanıma başlatılıyor...", "info")
            
            # Set flags
            self.running = True
            self.voice_assistant.start_listening()
            
            # Start voice recognition in a separate thread
            if not self.listen_thread or not self.listen_thread.is_alive():
                self.listen_thread = threading.Thread(target=self.run_async_loop, daemon=True)
                self.listen_thread.start()
                logger.debug("Voice recognition thread started")
            
        except Exception as e:
            logger.error(f"Error starting voice recognition: {e}\n{traceback.format_exc()}")
            self.ui.log_message("Ses tanıma başlatılamadı", "error")
    
    def stop_listening(self):
        """Stop the voice recognition loop"""
        try:
            logger.info("Stopping voice recognition")
            
            # Set flags
            self.running = False
            self.voice_assistant.stop_listening()
            self.ui.log_message("Ses tanıma durduruluyor...", "warning")
            
            # Wait for thread to finish if it exists
            if self.listen_thread and self.listen_thread.is_alive():
                logger.debug("Waiting for voice recognition thread to finish")
                self.listen_thread.join(timeout=2.0)
                if self.listen_thread.is_alive():
                    logger.warning("Voice recognition thread did not finish in time")
                
            logger.debug("Voice recognition stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping voice recognition: {e}\n{traceback.format_exc()}")
            
    def run(self):
        """Start the application"""
        try:
            logger.info("Starting Lazzaran Voice Assistant")
            self.ui.log_message("Lazzaran Sesli Asistan'a hoş geldiniz!", "success")
            self.ui.run()
        except Exception as e:
            logger.error(f"Application error: {e}\n{traceback.format_exc()}")
            self.ui.log_message(f"Kritik hata: {str(e)}", "error")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources")
        try:
            # Stop voice recognition if running
            if self.running:
                self.stop_listening()
            
            # Save conversation history
            conversation_file = self.config.temp_directory / "last_conversation.json"
            self.ai_service.save_conversation(str(conversation_file))
            logger.debug("Conversation history saved")
            
            # Cleanup temporary files
            for file in self.config.temp_directory.glob("*.mp3"):
                try:
                    if file.exists():
                        file.unlink()
                        logger.debug(f"Deleted temporary file: {file}")
                except Exception as e:
                    logger.warning(f"Error deleting temp file {file}: {e}")
            
            # Stop music if playing
            self.system_service.stop_music()
            logger.debug("Music playback stopped")
            
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
            logger.debug("Thread pool executor shut down")
            
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        app = LazzaranApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}\n{traceback.format_exc()}")
        sys.exit(1) 