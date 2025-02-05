"""
Command handler module for processing voice commands and executing corresponding actions.
"""

import webbrowser
import subprocess
import os
from typing import Optional, Dict, Callable, List
import logging
import traceback
from pathlib import Path
from datetime import datetime
import requests
from dataclasses import dataclass
import asyncio
from .services.weather import WeatherService
from .services.news import NewsService
from .services.ai_service import AIService
from .services.system_service import SystemService
import re
from concurrent.futures import ThreadPoolExecutor

@dataclass
class CommandContext:
    """Context object for command execution"""
    command: str
    params: dict = None
    
class CommandHandler:
    def __init__(self, weather_service: WeatherService, news_service: NewsService, 
                 ai_service: AIService, system_service: SystemService):
        """Initialize CommandHandler"""
        self.logger = logging.getLogger(__name__)
        self._commands = {}
        self._command_aliases = {}  # Initialize empty dictionary for aliases
        
        # Set up services
        self.weather_service = weather_service
        self.news_service = news_service
        self.ai_service = ai_service
        self.system_service = system_service
        
        # Initialize thread pool
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Register default commands first
        self._register_default_commands()
        
        # Then register command aliases
        self._register_command_aliases()
    
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
            "sohbet": self._chat_with_ai,
            "uygulama_ac": self._open_application_with_ai
        })
    
    def _register_command_aliases(self):
        """Register command aliases"""
        self._command_aliases.update({
            # News commands
            "haber ver": "haberler",
            "haberleri göster": "haberler",
            
            # Weather commands
            "havayı söyle": "hava durumu",
            "hava nasıl": "hava durumu",
            
            # Time commands
            "saat kaç": "saat",
            "saati söyle": "saat",
            
            # System commands
            "bilgisayarı kapat": "kapat",
            "sistemi kapat": "kapat",
            "yeniden başlat": "restart",
            
            # Application commands
            "hesap makinesini aç": "calculator",
            "not defterini aç": "notepad",
            "google'ı aç": "google",
            "youtube'u aç": "youtube",
            "spotify'ı aç": "spotify",
            "müzik aç": "spotify",
            "tarayıcıyı aç": "chrome",
            "chrome'u aç": "chrome",
            "firefox'u aç": "firefox",
            "word'ü aç": "word",
            "excel'i aç": "excel",
            "powerpoint'i aç": "powerpoint",
            "vscode'u aç": "vscode",
            "teams'i aç": "teams",
            "dosya gezginini aç": "explorer",
            "görev yöneticisini aç": "taskmgr",
            "denetim masasını aç": "control",
            
            # Generic application commands
            "uygulamayı aç": "uygulama_ac",
            "programı aç": "uygulama_ac",
            "açar mısın": "uygulama_ac"
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
        for alias, command in self._command_aliases.items():
            if alias in text:
                return command
                
        return None
        
    def _get_app_name_from_command(self, command: str) -> Optional[str]:
        """Extract application name from command"""
        # Application opening keywords
        app_keywords = {"aç", "başlat", "çalıştır", "göster", "hazır"}
        
        # Common application names and their aliases
        APP_ALIASES = {
            # Browsers
            "chrome": ["chrome", "google chrome", "tarayıcı", "browser"],
            "firefox": ["firefox", "mozilla"],
            "opera": ["opera", "opera gx", "opera browser"],
            "edge": ["edge", "microsoft edge"],
            
            # Office Apps
            "word": ["word", "microsoft word", "kelime işlemci"],
            "excel": ["excel", "microsoft excel", "hesap tablosu"],
            "powerpoint": ["powerpoint", "microsoft powerpoint", "sunu", "sunum"],
            
            # Development
            "vscode": ["vscode", "visual studio code", "vs code", "visual studio"],
            
            # Communication
            "teams": ["teams", "microsoft teams"],
            "discord": ["discord", "dc"],
            "skype": ["skype"],
            "telegram": ["telegram"],
            "whatsapp": ["whatsapp", "wp"],
            
            # Media & Entertainment
            "spotify": ["spotify", "müzik"],
            "steam": ["steam", "valve"],
            "epic": ["epic", "epic games"],
            "vlc": ["vlc", "vlc player", "media player"],
            
            # System Apps
            "notepad": ["notepad", "not defteri", "not", "notlar"],
            "calculator": ["calculator", "hesap makinesi", "hesap", "hesapla", "hesaplayıcı"],
            "paint": ["paint", "resim", "çizim"],
            "cmd": ["cmd", "komut istemi", "terminal", "command prompt"],
            "explorer": ["explorer", "dosya gezgini", "gezgin", "dosyalar"],
            "taskmgr": ["task manager", "görev yöneticisi", "görevler"],
            "control": ["control panel", "denetim masası", "kontrol", "ayarlar"]
        }

        # Split command into words
        words = command.lower().split()
        
        # Check if command contains an opening keyword
        if not any(keyword in words for keyword in app_keywords):
            return None
            
        # Get the part after the keyword
        for i, word in enumerate(words):
            if word in app_keywords:
                app_phrase = " ".join(words[:i] + words[i+1:])  # Tüm kelimeleri al, anahtar kelime hariç
                break
        else:
            return None
            
        # Check for direct matches in aliases
        for app_name, aliases in APP_ALIASES.items():
            if any(alias in app_phrase for alias in aliases) or any(alias in command for alias in aliases):
                return app_name
                
        # If no match found in aliases, try AI-based matching
        return None

    async def process_command(self, command: str) -> str:
        """Process a voice command and return the response"""
        try:
            command = command.lower().strip()
            
            # First check for application opening commands
            app_name = self._get_app_name_from_command(command)
            if app_name:
                # Eğer hesap makinesi ise ve "hazır" kelimesi varsa özel yanıt ver
                if app_name == "calculator" and "hazır" in command:
                    return "Hesap makinesi hazır! Ne hesaplamak istersin?"
                    
                # Uygulamayı başlat
                success = self.system_service.launch_application(app_name)
                
                # Özel yanıtlar
                app_responses = {
                    "discord": "Discord'u senin için açıyorum. İyi eğlenceler!",
                    "steam": "Steam'i başlatıyorum. İyi oyunlar!",
                    "opera": "Opera tarayıcını açıyorum. Keyifli tarama!",
                    "spotify": "Spotify açılıyor. Keyifli dinlemeler!",
                    "chrome": "Chrome tarayıcını açıyorum. İyi gezinmeler!",
                    "firefox": "Firefox tarayıcını açıyorum. İyi gezinmeler!",
                    "vscode": "Visual Studio Code başlatılıyor. İyi kodlamalar!",
                    "notepad": "Not defteri açılıyor. İyi notlar!",
                    "calculator": "Hesap makinesi açılıyor. İyi hesaplamalar!"
                }
                
                if success:
                    return app_responses.get(app_name, f"{app_name.title()} başarıyla açıldı.")
                else:
                    return f"Üzgünüm, {app_name.title()} uygulaması bilgisayarınızda bulunamadı veya açılamadı."
            
            # Check for web commands
            if "youtube" in command:
                return self._open_youtube(CommandContext(command=command))
            elif "google" in command:
                return self._open_google(CommandContext(command=command))
            
            # Check for other commands
            command_key = self._find_matching_command(command)
            if command_key and command_key in self._commands:
                return await self._execute_command(
                    self._commands[command_key],
                    CommandContext(command=command)
                )
            
            # If no command matches, use AI
            return await self._chat_with_ai(CommandContext(command=command))
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
    
    async def _execute_command(self, handler: Callable, context: CommandContext) -> str:
        """Execute a command handler safely"""
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler(context)
            else:
                # Sync fonksiyonları async olarak çalıştır
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, handler, context)
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
    
    async def _open_application_with_ai(self, context: CommandContext) -> str:
        """AI yardımıyla uygulamayı açar"""
        try:
            # AI'dan uygulama adını analiz etmesini iste
            ai_prompt = f"""
            Aşağıdaki komuttan açılması istenen uygulamanın adını belirle:
            Komut: "{context.command}"
            
            Lütfen sadece uygulama adını döndür, başka bir şey yazma.
            Örnek yanıt formatları: 
            - "chrome"
            - "notepad"
            - "calculator"
            - "spotify"
            
            Eğer uygulama adı belirlenemezse sadece "unknown" döndür.
            """
            
            app_name = await self.ai_service.get_response(ai_prompt)
            self.logger.info(f"AI returned app name: {app_name}")
            
            if not app_name or app_name.lower() == "unknown":
                return "Üzgünüm, açmak istediğiniz uygulamayı anlayamadım."
            
            app_name = app_name.strip().lower()
            
            # Uygulamayı başlat
            if self.system_service.launch_application(app_name):
                return f"{app_name.title()} uygulaması başarıyla açıldı."
            else:
                return f"Üzgünüm, {app_name.title()} uygulaması bilgisayarınızda bulunamadı veya açılamadı."
                
        except Exception as e:
            self.logger.error(f"Error in AI-assisted application opening: {e}")
            return "Uygulama açma işlemi sırasında bir hata oluştu" 