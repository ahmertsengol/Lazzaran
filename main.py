"""
Main entry point for the Lazzaran Voice Assistant application.
"""

import logging
import sys
import asyncio
from pathlib import Path
import traceback
from concurrent.futures import ThreadPoolExecutor
from core.voice_assistant import VoiceAssistant, VoiceAssistantConfig
from core.command_handler import CommandHandler
from core.services.weather import WeatherService
from core.services.news import NewsService
from core.services.ai_service import AIService
from ui.display import VoiceAssistantUI
from config.settings import ConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('lazzaran.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class LazzaranApp:
    def __init__(self):
        try:
            self.config = ConfigManager()
            self.setup_components()
            self.executor = ThreadPoolExecutor(max_workers=3)
            self.running = True
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise
        
    def setup_components(self):
        """Initialize all application components"""
        try:
            # Initialize voice assistant
            voice_config = VoiceAssistantConfig(
                language=self.config.voice_settings.language,
                timeout=self.config.voice_settings.timeout,
                ambient_duration=self.config.voice_settings.ambient_duration,
                temp_audio_file=str(self.config.temp_directory / "response.mp3")
            )
            self.voice_assistant = VoiceAssistant(config=voice_config)
            
            # Initialize services
            self.weather_service = WeatherService(
                api_key=self.config.api_keys.weather_api_key,
                language=self.config.voice_settings.language.split('-')[0]
            )
            
            self.news_service = NewsService(
                api_key=self.config.api_keys.news_api_key,
                language=self.config.voice_settings.language.split('-')[0]
            )
            
            self.ai_service = AIService(
                api_key=self.config.api_keys.gemini_api_key
            )
            
            # Initialize command handler with services
            self.command_handler = CommandHandler(
                weather_service=self.weather_service,
                news_service=self.news_service,
                ai_service=self.ai_service
            )
            
            # Initialize UI
            self.ui = VoiceAssistantUI(
                on_start=self.start_listening,
                on_stop=self.stop_listening
            )
        except Exception as e:
            logger.error(f"Component setup error: {e}")
            raise
        
    async def process_voice_command(self, text: str):
        """Process voice command asynchronously"""
        if not text:
            return
            
        try:
            response = await self.command_handler.process_command(text)
            if response:
                self.ui.log_message(f"Lazzaran: {response}", "success")
                await self.speak_response(response)
        except Exception as e:
            error_msg = f"Komut işlenirken hata oluştu: {str(e)}"
            logger.error(f"Command processing error: {e}\n{traceback.format_exc()}")
            self.ui.log_message(error_msg, "error")
            await self.speak_response("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.")
    
    async def speak_response(self, text: str):
        """Speak the response asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self.voice_assistant.speak, text)
        except Exception as e:
            logger.error(f"Speech output error: {e}")
            self.ui.log_message("Ses çıkışı sırasında bir hata oluştu", "error")
        
    def start_listening(self):
        """Start the voice recognition loop"""
        try:
            logger.info("Starting voice recognition")
            self.ui.log_message("Ses tanıma başlatılıyor...", "info")
            self.running = True
            
            async def listen_loop():
                while self.running and self.ui.is_listening:
                    try:
                        text = self.voice_assistant.listen()
                        if text:
                            self.ui.log_message(f"Siz: {text}", "info")
                            await self.process_voice_command(text)
                    except Exception as e:
                        logger.error(f"Voice recognition error: {e}\n{traceback.format_exc()}")
                        self.ui.log_message("Ses tanıma sırasında bir hata oluştu. Yeniden başlatılıyor...", "error")
                        await asyncio.sleep(1)  # Prevent rapid retries
            
            # Run the async loop in a separate thread
            asyncio.run(listen_loop())
        except Exception as e:
            logger.error(f"Error starting voice recognition: {e}")
            self.ui.log_message("Ses tanıma başlatılamadı", "error")
    
    def stop_listening(self):
        """Stop the voice recognition loop"""
        try:
            logger.info("Stopping voice recognition")
            self.running = False
            self.ui.log_message("Ses tanıma durduruluyor...", "warning")
        except Exception as e:
            logger.error(f"Error stopping voice recognition: {e}")
    
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
            # Save conversation history
            conversation_file = self.config.temp_directory / "last_conversation.json"
            self.ai_service.save_conversation(str(conversation_file))
            
            # Cleanup temporary files
            for file in self.config.temp_directory.glob("*.mp3"):
                try:
                    if file.exists():
                        file.unlink()
                except Exception as e:
                    logger.warning(f"Error deleting temp file {file}: {e}")
            
            # Shutdown thread pool
            self.executor.shutdown(wait=False)
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

if __name__ == "__main__":
    try:
        app = LazzaranApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}\n{traceback.format_exc()}")
        sys.exit(1) 