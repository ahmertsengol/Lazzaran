import logging
import traceback
import tkinter as tk
from tkinter import ttk, scrolledtext

class VoiceAssistantUI:
    def __init__(self, system_service):
        """Initialize the UI components."""
        try:
            self.logger = logging.getLogger(__name__)
            self.logger.info("Initializing Voice Assistant UI...")
            
            self.system_service = system_service
            self.root = tk.Tk()
            self.root.title("Lazzaran Voice Assistant")
            
            # Dark theme colors
            self.bg_color = "#2b2b2b"
            self.fg_color = "#ffffff"
            self.button_bg = "#404040"
            self.button_active_bg = "#4a4a4a"
            
            self.root.configure(bg=self.bg_color)
            
            # Configure styles
            self.style = ttk.Style()
            self.style.configure("Custom.TButton",
                               background=self.button_bg,
                               foreground=self.fg_color,
                               padding=5)
            
            # Create and pack the button frame
            self.button_frame = ttk.Frame(self.root)
            self.button_frame.pack(pady=10)
            
            # Create buttons
            self.start_button = ttk.Button(
                self.button_frame,
                text="Başlat",
                style="Custom.TButton",
                command=self.system_service.start_listening
            )
            self.start_button.pack(side=tk.LEFT, padx=5)
            
            self.stop_button = ttk.Button(
                self.button_frame,
                text="Durdur",
                style="Custom.TButton",
                command=self.system_service.stop_listening
            )
            self.stop_button.pack(side=tk.LEFT, padx=5)
            
            self.stop_speech_button = ttk.Button(
                self.button_frame,
                text="Sustur",
                style="Custom.TButton",
                command=self.stop_speaking
            )
            self.stop_speech_button.pack(side=tk.LEFT, padx=5)
            
            # Create console output
            self.console = scrolledtext.ScrolledText(
                self.root,
                wrap=tk.WORD,
                width=50,
                height=20,
                bg=self.bg_color,
                fg=self.fg_color
            )
            self.console.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            self.logger.info("Voice Assistant UI initialized successfully")
            
        except Exception as e:
            self.logger.critical(f"Failed to initialize UI: {e}\n{traceback.format_exc()}")
            raise

    def stop_speaking(self):
        """Stop the current speech output."""
        try:
            self.logger.info("Stopping speech output...")
            self.system_service.stop_speaking()
            self.log_message("Konuşma durduruldu.")
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}\n{traceback.format_exc()}")
            self.log_message("Konuşma durdurulamadı: " + str(e)) 