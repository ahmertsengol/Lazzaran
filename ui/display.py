"""
Modern UI component for the voice assistant using tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Callable, Optional
from datetime import datetime
import json
from pathlib import Path
from core.services.system_service import SystemService, ApplicationInfo
import logging
import traceback

logger = logging.getLogger(__name__)

class VoiceAssistantUI:
    def __init__(self, system_service: SystemService, on_start: Callable = None, on_stop: Callable = None):
        try:
            logger.info("Initializing voice assistant UI...")
            
            self.root = tk.Tk()
            self.root.title("Lazzaran Voice Assistant")
            self.root.geometry("1000x500")  # Daha geniş ve kısa pencere
            
            # Pencere minimum boyutu
            self.root.minsize(800, 400)
            
            # Pencereyi ekranın ortasında başlat
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 1000) // 2
            y = (screen_height - 500) // 2
            self.root.geometry(f"1000x500+{x}+{y}")
            
            self.setup_theme()
            
            self.system_service = system_service
            self.on_start = on_start
            self.on_stop = on_stop
            self.is_listening = False
            
            # Yükleme ekranı için değişkenler
            self.loading_window = None
            self.loading_canvas = None
            self.loading_progress = 0
            self.loading_text = ""
            self.loading_steps = [
                "Dinleme durduruluyor...",
                "Konsol temizleniyor...",
                "Uygulamalar yenileniyor...",
                "Sistem yeniden başlatılıyor...",
                "Tamamlandı!"
            ]
            
            # Uygulama kapatma işlevi için protokol ekle
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self.setup_ui()
            
            logger.info("Voice assistant UI initialized successfully")
            
        except Exception as e:
            logger.critical(f"UI initialization failed: {e}\n{traceback.format_exc()}")
            raise
        
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
            foreground='#ffffff',
            padding=5)
            
        style.map('TButton',
            background=[('active', '#505050')])
            
        # Treeview stilleri
        style.configure("Treeview",
            background="#1e1e1e",
            foreground="#ffffff",
            fieldbackground="#1e1e1e")
        
        style.configure("Treeview.Heading",
            background="#404040",
            foreground="#ffffff")
            
        style.map("Treeview",
            background=[('selected', '#404040')],
            foreground=[('selected', '#ffffff')])
            
    def setup_ui(self):
        """Setup the main UI components"""
        # Ana pencereyi iki panele böl
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))
        
        # Sol panel - Asistan kontrolleri
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)
        
        # Status frame
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=('Segoe UI', 12)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(
            status_frame,
            text="",
            font=('Segoe UI', 12)
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Console output
        self.console = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            width=40,
            height=10,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 11)
        )
        self.console.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Control buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X)
        
        # Özel buton stilleri
        style = ttk.Style()
        style.configure("Start.TButton",
            background='#28a745',
            foreground='white',
            padding=8,
            font=('Segoe UI', 10, 'bold')
        )
        
        style.configure("Stop.TButton",
            background='#dc3545',
            foreground='white',
            padding=8,
            font=('Segoe UI', 10, 'bold')
        )
        
        # Dinleme başlat/durdur butonu
        self.start_button = ttk.Button(
            button_frame,
            text="Start Listening",
            style="Start.TButton",
            command=self.toggle_listening
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Konuşmayı durdur butonu
        style.configure("StopSpeech.TButton",
            background='#ffc107',
            foreground='black',
            padding=8,
            font=('Segoe UI', 10, 'bold')
        )
        
        self.stop_speech_button = ttk.Button(
            button_frame,
            text="Konuşmayı Durdur",
            style="StopSpeech.TButton",
            command=self.stop_speaking
        )
        self.stop_speech_button.pack(side=tk.LEFT, padx=5)
        
        # Reset butonu
        style.configure("Reset.TButton",
            background='#ffd700',
            foreground='black',
            padding=8,
            font=('Segoe UI', 10, 'bold')
        )
        
        ttk.Button(
            button_frame,
            text="Asistanı Resetle",
            style="Reset.TButton",
            command=self.reset_assistant
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear Console",
            command=self.clear_console
        ).pack(side=tk.LEFT, padx=5)
        
        # Sağ panel - Uygulama listesi
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=1)
        
        # Uygulama listesi başlığı ve yenileme butonu
        app_header_frame = ttk.Frame(right_frame)
        app_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            app_header_frame,
            text="Uygulamalar",
            font=('Segoe UI', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            app_header_frame,
            text="Yenile",
            command=self.refresh_app_list
        ).pack(side=tk.RIGHT)
        
        # Uygulama kontrol butonları - Üst kısma taşındı
        app_control_frame = ttk.Frame(right_frame)
        app_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Başlat butonu - Yeşil ve büyük
        style.configure("LaunchApp.TButton",
            background='#28a745',
            foreground='white',
            padding=10,
            font=('Segoe UI', 11, 'bold')
        )
        
        ttk.Button(
            app_control_frame,
            text="Uygulamayı Başlat",
            style="LaunchApp.TButton",
            command=self.launch_selected_app
        ).pack(side=tk.LEFT, padx=5)
        
        # Kapat butonu - Kırmızı ve büyük
        style.configure("TerminateApp.TButton",
            background='#dc3545',
            foreground='white',
            padding=10,
            font=('Segoe UI', 11, 'bold')
        )
        
        ttk.Button(
            app_control_frame,
            text="Uygulamayı Kapat",
            style="TerminateApp.TButton",
            command=self.terminate_selected_app
        ).pack(side=tk.RIGHT, padx=5)
        
        # Uygulama listesi
        self.app_tree = ttk.Treeview(
            right_frame,
            columns=('name', 'status', 'description'),
            show='headings',
            selectmode='browse'
        )
        
        # Sütun başlıkları
        self.app_tree.heading('name', text='Uygulama')
        self.app_tree.heading('status', text='Durum')
        self.app_tree.heading('description', text='Açıklama')
        
        # Sütun genişlikleri
        self.app_tree.column('name', width=150)
        self.app_tree.column('status', width=100)
        self.app_tree.column('description', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.app_tree.yview)
        self.app_tree.configure(yscrollcommand=scrollbar.set)
        
        self.app_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Başlangıç listesini yükle
        self.refresh_app_list()
        
        # Start time updates
        self.update_time()
        
        # Alt kısma kapatma butonu ekle
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Özel stil tanımla
        style.configure("Exit.TButton",
            background='#dc3545',
            foreground='white',
            padding=10,
            font=('Segoe UI', 10, 'bold')
        )
        
        exit_button = ttk.Button(
            bottom_frame,
            text="Asistanı Kapat",
            style="Exit.TButton",
            command=self.on_closing
        )
        exit_button.pack(side=tk.RIGHT)
    
    def refresh_app_list(self):
        """Uygulama listesini yenile"""
        try:
            # Mevcut seçili uygulamayı hatırla
            selected_items = self.app_tree.selection()
            selected_exe = None
            if selected_items:
                selected_exe = self.app_tree.item(selected_items[0])['tags'][0]

            # Mevcut listeyi temizle
            for item in self.app_tree.get_children():
                self.app_tree.delete(item)
            
            # Uygulamaları listele
            for app in self.system_service.get_available_applications():
                status = "Çalışıyor" if app.is_running else "Durgun"
                self.app_tree.insert('', tk.END, values=(app.name, status, app.description), tags=(app.exe_name,))
                
            # Önceki seçimi geri yükle
            if selected_exe:
                for item in self.app_tree.get_children():
                    if selected_exe in self.app_tree.item(item)['tags']:
                        self.app_tree.selection_set(item)
                        self.app_tree.see(item)
                        break
                        
        except Exception as e:
            self.log_message(f"Uygulama listesi güncellenirken hata oluştu: {str(e)}", "error")
    
    def launch_selected_app(self):
        """Seçili uygulamayı başlat"""
        selection = self.app_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir uygulama seçin")
            return
            
        item = selection[0]
        exe_name = self.app_tree.item(item)['tags'][0]
        
        if self.system_service.launch_application(exe_name):
            self.log_message(f"{exe_name} uygulaması başlatıldı", "success")
            self.refresh_app_list()
        else:
            self.log_message(f"{exe_name} uygulaması başlatılamadı", "error")
    
    def terminate_selected_app(self):
        """Seçili uygulamayı sonlandır"""
        selection = self.app_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir uygulama seçin")
            return
            
        item = selection[0]
        exe_name = self.app_tree.item(item)['tags'][0]
        
        if self.system_service.terminate_application(exe_name):
            self.log_message(f"{exe_name} uygulaması kapatıldı", "success")
            self.refresh_app_list()
        else:
            self.log_message(f"{exe_name} uygulaması kapatılamadı", "error")
    
    def toggle_listening(self):
        """Toggle listening state"""
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.start_button.configure(text="Stop Listening", style="Stop.TButton")
            self.status_label.configure(text="Listening...")
            if self.on_start:
                threading.Thread(target=self.on_start).start()
        else:
            self.start_button.configure(text="Start Listening", style="Start.TButton")
            self.status_label.configure(text="Ready")
            if self.on_stop:
                self.on_stop()
    
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
    
    def log_message(self, message: str, level: str = "info"):
        """Add a message to the log display."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            
            self.console.insert(tk.END, formatted_message, level)
            self.console.see(tk.END)
            
            # Also log to system logger
            log_level = getattr(logging, level.upper(), logging.INFO)
            logger.log(log_level, message)
            
        except Exception as e:
            logger.error(f"Error logging message: {e}\n{traceback.format_exc()}")
    
    def clear_console(self):
        """Clear the console output"""
        self.console.delete(1.0, tk.END)
    
    def run(self):
        """Start the UI main loop"""
        try:
            logger.info("Starting UI main loop")
            self.root.mainloop()
            logger.info("UI main loop ended")
        except Exception as e:
            logger.critical(f"UI main loop error: {e}\n{traceback.format_exc()}")
            raise
    
    def stop(self):
        """Stop the UI"""
        self.root.quit()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Çıkış", "Sesli asistanı kapatmak istediğinize emin misiniz?"):
            # Dinlemeyi durdur
            if self.is_listening and self.on_stop:
                self.on_stop()
            
            self.log_message("Lazzaran Sesli Asistan kapatılıyor...", "warning")
            self.root.after(1000, self.root.destroy)  # 1 saniye bekleyip kapat
    
    def show_loading_screen(self):
        """Profesyonel yükleme ekranını göster"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Yeniden Başlatılıyor")
        
        # Pencere boyutu ve konumu
        window_width = 400
        window_height = 200
        x = self.root.winfo_x() + (self.root.winfo_width() - window_width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - window_height) // 2
        self.loading_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Pencere özellikleri
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        self.loading_window.configure(bg='#1e1e1e')
        
        # Canvas oluştur
        self.loading_canvas = tk.Canvas(
            self.loading_window,
            width=window_width,
            height=window_height,
            bg='#1e1e1e',
            highlightthickness=0
        )
        self.loading_canvas.pack(fill=tk.BOTH, expand=True)
        
        # İlerleme çubuğu boyutları
        bar_width = 300
        bar_height = 6
        x1 = (window_width - bar_width) // 2
        y1 = window_height // 2
        
        # Arka plan çubuğu
        self.loading_canvas.create_rectangle(
            x1, y1,
            x1 + bar_width, y1 + bar_height,
            fill='#333333',
            width=0
        )
        
        # İlerleme çubuğu
        self.progress_bar = self.loading_canvas.create_rectangle(
            x1, y1,
            x1, y1 + bar_height,
            fill='#007acc',
            width=0,
            tags='progress'
        )
        
        # Yüzde metni
        self.progress_text = self.loading_canvas.create_text(
            window_width // 2, y1 + 30,
            text="0%",
            fill='#ffffff',
            font=('Segoe UI', 10),
            tags='progress_text'
        )
        
        # Durum metni
        self.status_text = self.loading_canvas.create_text(
            window_width // 2, y1 - 30,
            text=self.loading_steps[0],
            fill='#ffffff',
            font=('Segoe UI', 11, 'bold'),
            tags='status_text'
        )
        
        # Logo veya ikon (örnek olarak daire)
        self.loading_canvas.create_oval(
            window_width//2 - 40, 30,
            window_width//2 + 40, 110,
            outline='#007acc',
            width=2
        )
        
        # Logo içi text
        self.loading_canvas.create_text(
            window_width//2, 70,
            text="L",
            fill='#007acc',
            font=('Segoe UI', 36, 'bold')
        )
    
    def update_loading_progress(self, step: int):
        """Yükleme ekranını güncelle"""
        if self.loading_canvas:
            # İlerleme yüzdesi
            progress = (step + 1) * 20  # Her adım %20
            self.loading_progress = progress
            
            # İlerleme çubuğunu güncelle
            bar_width = 300
            x1 = (400 - bar_width) // 2
            y1 = 200 // 2
            self.loading_canvas.coords(
                self.progress_bar,
                x1, y1,
                x1 + (bar_width * progress / 100), y1 + 6
            )
            
            # Metinleri güncelle
            self.loading_canvas.itemconfig(
                self.progress_text,
                text=f"%{progress}"
            )
            
            if step < len(self.loading_steps):
                self.loading_canvas.itemconfig(
                    self.status_text,
                    text=self.loading_steps[step]
                )
            
            # Ekranı güncelle
            self.loading_window.update()
    
    def close_loading_screen(self):
        """Yükleme ekranını kapat"""
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None
            self.loading_canvas = None
    
    def reset_assistant(self):
        """Asistanı resetle"""
        if messagebox.askokcancel("Reset", 
            "Sesli asistanı resetlemek istediğinize emin misiniz?\n\n"
            "Bu işlem:\n"
            "• Dinlemeyi durduracak\n"
            "• Konsolu temizleyecek\n"
            "• Uygulamaları yenileyecek\n"
            "• Sistemi yeniden başlatacak"):
            
            # Yükleme ekranını göster
            self.show_loading_screen()
            
            def reset_thread():
                try:
                    # Adım 1: Dinlemeyi durdur
                    if self.is_listening:
                        self.root.after(0, self.toggle_listening)
                    self.root.after(0, lambda: self.update_loading_progress(0))
                    self.root.after(500)
                    
                    # Adım 2: Konsolu temizle
                    self.root.after(0, self.clear_console)
                    self.root.after(0, lambda: self.update_loading_progress(1))
                    self.root.after(500)
                    
                    # Adım 3: Uygulamaları yenile
                    self.root.after(0, self.system_service.refresh_application_list)
                    self.root.after(0, lambda: self.update_loading_progress(2))
                    self.root.after(500)
                    
                    # Adım 4: Listeyi güncelle
                    self.root.after(0, self.refresh_app_list)
                    self.root.after(0, lambda: self.update_loading_progress(3))
                    self.root.after(500)
                    
                    # Adım 5: Tamamlandı
                    self.root.after(0, lambda: self.status_label.configure(text="Ready"))
                    self.root.after(0, lambda: self.update_loading_progress(4))
                    self.root.after(1000)
                    
                    # Yükleme ekranını kapat
                    self.root.after(0, self.close_loading_screen)
                    
                    # Başarı mesajı
                    self.root.after(0, lambda: self.log_message(
                        "✓ Sesli asistan başarıyla resetlendi",
                        "success"
                    ))
                    
                except Exception as e:
                    # Hata durumunda
                    self.root.after(0, self.close_loading_screen)
                    self.root.after(0, lambda: self.log_message(
                        f"Reset sırasında hata oluştu: {str(e)}",
                        "error"
                    ))
            
            # Thread'i başlat
            threading.Thread(target=reset_thread).start() 
    
    def stop_speaking(self):
        """Stop current speech output"""
        try:
            logger.debug("Stopping speech output...")
            self.system_service.stop_speaking()
            self.log_message("Konuşma durduruldu", "info")
        except Exception as e:
            logger.error(f"Error stopping speech: {e}\n{traceback.format_exc()}")
            self.log_message("Konuşma durdurulamadı", "error") 