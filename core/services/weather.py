"""
Weather service for fetching and formatting weather information.
"""

import requests
import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WeatherInfo:
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    location: str
    timestamp: datetime

class WeatherService:
    def __init__(self, api_key: str, language: str = 'tr'):
        self.api_key = api_key
        self.language = language
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city: str) -> Optional[WeatherInfo]:
        """
        Fetch weather information for a given city.
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'lang': self.language,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return WeatherInfo(
                temperature=data['main']['temp'],
                condition=data['weather'][0]['description'],
                humidity=data['main']['humidity'],
                wind_speed=data['wind']['speed'],
                location=data['name'],
                timestamp=datetime.now()
            )
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching weather data: {e}")
            return None
        except KeyError as e:
            self.logger.error(f"Error parsing weather data: {e}")
            return None
    
    def format_weather_response(self, weather: WeatherInfo) -> str:
        """
        Format weather information into a readable response.
        """
        if not weather:
            return "Üzgünüm, hava durumu bilgisi alınamadı."
        
        # Capitalize the first letter of condition
        condition = weather.condition[0].upper() + weather.condition[1:]
        
        return (
            f"{weather.location} için hava durumu:\n"
            f"• Sıcaklık: {weather.temperature:.1f}°C\n"
            f"• Durum: {condition}\n"
            f"• Nem: %{weather.humidity}\n"
            f"• Rüzgar Hızı: {weather.wind_speed:.1f} m/s"
        ) 