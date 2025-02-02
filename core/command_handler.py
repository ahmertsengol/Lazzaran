"""
Command handler module for processing voice commands and executing corresponding actions.
"""

import webbrowser
import subprocess
from typing import Optional, Dict, Callable, List
import logging
import traceback
from pathlib import Path
from datetime import datetime
import requests
from dataclasses import dataclass
from .services.weather import WeatherService
from .services.news import NewsService
from .services.ai_service import AIService

@dataclass
class CommandContext:
    """Context object for command execution"""
    command: str
    params: dict = None
    
class CommandHandler:
    def __init__(self, weather_service: WeatherService, news_service: NewsService, ai_service: AIService):
        self.logger = logging.getLogger(__name__)
        self._commands: Dict[str, Callable] = {}
        self.weather_service = weather_service
        self.news_service = news_service
        self.ai_service = ai_service
        self._register_default_commands()
        
        # Command aliases for better recognition
        self.command_aliases = {
            "haber ver": "haberler",
            "haberleri göster": "haberler",
            "havayı söyle": "hava durumu",
            "saat kaç": "saat",
            "saati söyle": "saat",
            "bilgisayarı kapat": "kapat",
            "sistemi kapat": "kapat",
            "yeniden başlat": "restart",
            "hesap makinesini aç": "hesap makinesi",
            "google'ı aç": "google",
            "youtube'u aç": "youtube"
        }
    
    def _register_default_commands(self):
        """Register default command handlers"""
        self._commands.update({
            "google": self._open_google,
            "youtube": self._open_youtube,
            "hava durumu": self._get_weather,
            "saat": self._get_time,
            "kapat": self._shutdown_computer,
            "yeniden başlat": self._restart_computer,
            "hesap makinesi": self._open_calculator,
            "haberler": self._get_news,
            "haber ara": self._search_news,
            "sohbet": self._chat_with_ai
        })
    
    def register_command(self, keyword: str, handler: Callable):
        """Register a new command handler"""
        try:
            self._commands[keyword.lower()] = handler
        except Exception as e:
            self.logger.error(f"Error registering command '{keyword}': {e}")
            raise
        
    def _find_matching_command(self, text: str) -> Optional[str]:
        """Find the best matching command for the given text"""
        text = text.lower()
        
        # First check direct commands
        for keyword in self._commands.keys():
            if keyword in text:
                return keyword
        
        # Then check aliases
        for alias, command in self.command_aliases.items():
            if alias in text:
                return command
                
        return None
        
    async def process_command(self, text: str) -> Optional[str]:
        """Process a command and return the response"""
        if not text:
            return None
            
        try:
            # Find matching command
            command = self._find_matching_command(text)
            
            if command and command in self._commands:
                context = CommandContext(command=text)
                return await self._execute_command(self._commands[command], context)
            
            # If no direct command found, treat it as a conversation with AI
            return await self._chat_with_ai(CommandContext(command=text))
            
        except Exception as e:
            error_msg = f"Komut işlenirken hata oluştu: {str(e)}"
            self.logger.error(f"Command processing error: {e}\n{traceback.format_exc()}")
            return error_msg
    
    async def _execute_command(self, handler: Callable, context: CommandContext) -> str:
        """Execute a command handler safely"""
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler(context)
            else:
                return handler(context)
        except Exception as e:
            self.logger.error(f"Command execution error: {e}\n{traceback.format_exc()}")
            return f"Komut çalıştırılırken bir hata oluştu: {str(e)}"
    
    def _open_google(self, context: CommandContext) -> str:
        try:
            webbrowser.open("https://www.google.com")
            return "Google açılıyor"
        except Exception as e:
            self.logger.error(f"Error opening Google: {e}")
            return "Google açılırken bir hata oluştu"
    
    def _open_youtube(self, context: CommandContext) -> str:
        try:
            webbrowser.open("https://www.youtube.com")
            return "YouTube açılıyor"
        except Exception as e:
            self.logger.error(f"Error opening YouTube: {e}")
            return "YouTube açılırken bir hata oluştu"
    
    def _get_weather(self, context: CommandContext) -> str:
        try:
            # Extract city name from command
            words = context.command.lower().split()
            try:
                city_index = words.index("durumu") + 1
                city = words[city_index]
            except (ValueError, IndexError):
                city = "Istanbul"  # Default city
                
            weather_info = self.weather_service.get_weather(city)
            if weather_info:
                return self.weather_service.format_weather_response(weather_info)
            return "Hava durumu bilgisi alınamadı"
        except Exception as e:
            self.logger.error(f"Error getting weather: {e}")
            return "Hava durumu bilgisi alınırken bir hata oluştu"
    
    def _get_time(self, context: CommandContext) -> str:
        try:
            now = datetime.now()
            return f"Şu anki saat: {now.strftime('%H:%M:%S')}"
        except Exception as e:
            self.logger.error(f"Error getting time: {e}")
            return "Saat bilgisi alınırken bir hata oluştu"
    
    def _shutdown_computer(self, context: CommandContext) -> str:
        try:
            subprocess.run(["shutdown", "/s", "/t", "1"])
            return "Bilgisayar kapatılıyor"
        except Exception as e:
            self.logger.error(f"Error shutting down: {e}")
            return "Bilgisayar kapatılırken bir hata oluştu"
    
    def _restart_computer(self, context: CommandContext) -> str:
        try:
            subprocess.run(["shutdown", "/r", "/t", "1"])
            return "Bilgisayar yeniden başlatılıyor"
        except Exception as e:
            self.logger.error(f"Error restarting: {e}")
            return "Bilgisayar yeniden başlatılırken bir hata oluştu"
    
    def _open_calculator(self, context: CommandContext) -> str:
        try:
            subprocess.Popen(['calc.exe'])
            return "Hesap makinesi açılıyor"
        except Exception as e:
            self.logger.error(f"Error opening calculator: {e}")
            return "Hesap makinesi açılırken bir hata oluştu"
    
    def _get_news(self, context: CommandContext) -> str:
        try:
            # Extract category if specified
            words = context.command.lower().split()
            category = None
            categories = {
                "iş": "business",
                "eğlence": "entertainment",
                "sağlık": "health",
                "bilim": "science",
                "spor": "sports",
                "teknoloji": "technology"
            }
            
            for word in words:
                if word in categories:
                    category = categories[word]
                    break
                    
            articles = self.news_service.get_top_headlines(category=category)
            return self.news_service.format_articles_response(articles)
        except Exception as e:
            self.logger.error(f"Error getting news: {e}")
            return "Haberler alınırken bir hata oluştu"
    
    def _search_news(self, context: CommandContext) -> str:
        try:
            # Extract search query
            query = context.command.lower().replace("haber ara", "").strip()
            if not query:
                return "Arama yapmak için bir konu belirtmelisiniz"
                
            articles = self.news_service.search_news(query)
            return self.news_service.format_articles_response(articles, detailed=True)
        except Exception as e:
            self.logger.error(f"Error searching news: {e}")
            return "Haber araması yapılırken bir hata oluştu"
    
    async def _chat_with_ai(self, context: CommandContext) -> str:
        """Handle conversation with AI"""
        try:
            response = await self.ai_service.get_response(context.command)
            return response if response else "Üzgünüm, şu anda cevap veremiyorum"
        except Exception as e:
            self.logger.error(f"Error in AI chat: {e}")
            return "AI ile iletişim kurulurken bir hata oluştu" 