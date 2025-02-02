"""
AI service for handling conversations using Google's Gemini AI.
"""

import google.generativeai as genai
from typing import Optional, List, Dict
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Conversation:
    messages: List[Dict[str, str]]
    start_time: datetime
    last_update: datetime

class AIService:
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.setup_ai(api_key)
        self.conversation = None
        self.reset_conversation()
    
    def setup_ai(self, api_key: str):
        """Configure the Gemini AI client"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            # Set up initial context for Turkish responses
            initial_prompt = "Sen Türkçe konuşan bir sesli asistansın. Tüm yanıtlarını Türkçe olarak ver ve doğal, arkadaşça bir ton kullan."
            self.chat = self.model.start_chat(history=[{"role": "user", "parts": [initial_prompt]}])
        except Exception as e:
            self.logger.error(f"Error setting up Gemini AI: {e}")
            raise
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation = Conversation(
            messages=[],
            start_time=datetime.now(),
            last_update=datetime.now()
        )
    
    async def get_response(self, text: str) -> Optional[str]:
        """
        Get AI response for the given text input.
        """
        try:
            # Add user message to history
            self.conversation.messages.append({
                "role": "user",
                "content": text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get AI response
            response = self.chat.send_message(text)
            
            # Add AI response to history
            response_text = response.text
            self.conversation.messages.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            self.conversation.last_update = datetime.now()
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            return "Üzgünüm, şu anda isteğinizi işleyemiyorum. Lütfen daha sonra tekrar deneyin."
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the current conversation.
        """
        if not self.conversation.messages:
            return "Henüz konuşma geçmişi yok."
        
        duration = datetime.now() - self.conversation.start_time
        message_count = len(self.conversation.messages)
        
        return (
            f"Konuşma Özeti:\n"
            f"Süre: {duration.total_seconds() / 60:.1f} dakika\n"
            f"Mesaj Sayısı: {message_count}\n"
            f"Son güncelleme: {self.conversation.last_update.strftime('%H:%M:%S')}"
        )
    
    def save_conversation(self, filepath: str):
        """
        Save the current conversation to a file.
        """
        try:
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'messages': self.conversation.messages,
                    'start_time': self.conversation.start_time.isoformat(),
                    'last_update': self.conversation.last_update.isoformat()
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False 