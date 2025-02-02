"""
Modern UI component for the voice assistant using tkinter.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable
from datetime import datetime
import json
from pathlib import Path

class VoiceAssistantUI:
    def __init__(self, on_start: Callable = None, on_stop: Callable = None):
        self.root = tk.Tk()
        self.root.title("Lazzaran Voice Assistant")
        self.root.geometry("800x600")
        self.setup_theme()
        
        self.on_start = on_start
        self.on_stop = on_stop
        self.is_listening = False
        self.setup_ui()
        
    def setup_theme(self):
        """Setup dark theme for the application"""
        self.root.configure(bg='#2b2b2b')
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.',
            background='#2b2b2b',
            foreground='#ffffff',
            fieldbackground='#3b3b3b')
        
        style.configure('TButton',
            background='#404040',
            foreground='#ffffff')
            
        style.map('TButton',
            background=[('active', '#505050')])
            
    def setup_ui(self):
        """Setup the main UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=('Arial', 12)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(
            status_frame,
            text="",
            font=('Arial', 12)
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Console output
        self.console = tk.Text(
            main_frame,
            height=20,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 11)
        )
        self.console.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Listening",
            command=self.toggle_listening
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear Console",
            command=self.clear_console
        ).pack(side=tk.LEFT, padx=5)
        
        # Start time updates
        self.update_time()
        
    def toggle_listening(self):
        """Toggle listening state"""
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.start_button.configure(text="Stop Listening")
            self.status_label.configure(text="Listening...")
            if self.on_start:
                threading.Thread(target=self.on_start).start()
        else:
            self.start_button.configure(text="Start Listening")
            self.status_label.configure(text="Ready")
            if self.on_stop:
                self.on_stop()
    
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
    
    def log_message(self, message: str, message_type: str = "info"):
        """Log a message to the console with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different message types
        colors = {
            "info": "#ffffff",
            "error": "#ff6b6b",
            "success": "#69db7c",
            "warning": "#ffd43b"
        }
        
        self.console.tag_configure(message_type, foreground=colors.get(message_type, "#ffffff"))
        
        self.console.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.console.insert(tk.END, f"{message}\n", message_type)
        self.console.see(tk.END)
    
    def clear_console(self):
        """Clear the console output"""
        self.console.delete(1.0, tk.END)
    
    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()
    
    def stop(self):
        """Stop the UI"""
        self.root.quit() 