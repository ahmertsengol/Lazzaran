"""
System service for handling system operations like launching applications and playing media.
"""

import os
import subprocess
import platform
import logging
from pathlib import Path
import winreg
from typing import Optional, List, Dict
import pygame
import json
import glob
import psutil
from dataclasses import dataclass
import pythoncom  # COM için gerekli

@dataclass
class ApplicationInfo:
    name: str
    exe_name: str
    path: str
    is_running: bool
    description: str = ""
    icon_path: str = ""

class SystemService:
    def __init__(self, config_path: str = "config/system_paths.json"):
        self.logger = logging.getLogger(__name__)
        pygame.mixer.init()
        self.config_path = config_path
        self.system = platform.system()
        self.app_paths = self._load_app_paths()
        self.music_paths = self._load_music_paths()
        self.running_apps: Dict[str, subprocess.Popen] = {}
        self.discovered_apps: Dict[str, ApplicationInfo] = {}
        pythoncom.CoInitialize()  # COM'u başlat
        
        # Common Windows application paths
        self._COMMON_APPS = {
            "notepad.exe": "C:\\Windows\\System32\\notepad.exe",
            "calc.exe": "C:\\Windows\\System32\\calc.exe",
            "mspaint.exe": "C:\\Windows\\System32\\mspaint.exe",
            "cmd.exe": "C:\\Windows\\System32\\cmd.exe",
            "explorer.exe": "C:\\Windows\\explorer.exe",
            "taskmgr.exe": "C:\\Windows\\System32\\taskmgr.exe",
            "control.exe": "C:\\Windows\\System32\\control.exe",
            "chrome.exe": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "firefox.exe": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "WINWORD.EXE": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "EXCEL.EXE": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "POWERPNT.EXE": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
            "Code.exe": "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "Spotify.exe": "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe",
            "Teams.exe": "C:\\Users\\%USERNAME%\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe"
        }
        
        # Start initial scan
        self._initial_scan()
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            pythoncom.CoUninitialize()  # COM'u temizle
        except:
            pass
    
    def _initial_scan(self):
        """Initial scan for applications"""
        try:
            # Expand environment variables in paths
            for exe_name, path in self._COMMON_APPS.items():
                expanded_path = os.path.expandvars(path)
                self._COMMON_APPS[exe_name] = expanded_path
                
            # Scan for applications
            self._scan_for_applications()
            
        except Exception as e:
            self.logger.error(f"Application scan error: {e}")
    
    def _scan_for_applications(self):
        """Sistemde yüklü uygulamaları tara"""
        try:
            self.discovered_apps.clear()
            
            # Temel sistem uygulamaları
            basic_apps = {
                "notepad.exe": "C:\\Windows\\System32\\notepad.exe",
                "calc.exe": "C:\\Windows\\System32\\calc.exe",
                "mspaint.exe": "C:\\Windows\\System32\\mspaint.exe",
                "cmd.exe": "C:\\Windows\\System32\\cmd.exe",
                "explorer.exe": "C:\\Windows\\explorer.exe",
                "taskmgr.exe": "C:\\Windows\\System32\\taskmgr.exe",
                "control.exe": "C:\\Windows\\System32\\control.exe",
            }
            
            # Temel uygulamaları ekle
            for exe_name, path in basic_apps.items():
                if os.path.exists(path):
                    name = os.path.splitext(exe_name)[0].title()
                    self.discovered_apps[exe_name] = ApplicationInfo(
                        name=name,
                        exe_name=exe_name,
                        path=path,
                        is_running=self._is_process_running(exe_name),
                        description=self._get_file_description(path)
                    )
            
            # Yaygın program dizinleri
            common_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), "Google\\Chrome\\Application\\chrome.exe"),
                os.path.join(os.environ.get('PROGRAMFILES', ''), "Mozilla Firefox\\firefox.exe"),
                os.path.join(os.environ.get('PROGRAMFILES', ''), "Microsoft Office\\root\\Office16\\WINWORD.EXE"),
                os.path.join(os.environ.get('PROGRAMFILES', ''), "Microsoft Office\\root\\Office16\\EXCEL.EXE"),
                os.path.join(os.environ.get('PROGRAMFILES', ''), "Microsoft Office\\root\\Office16\\POWERPNT.EXE"),
                os.path.join(os.environ.get('APPDATA', ''), "Spotify\\Spotify.exe"),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), "Microsoft\\Teams\\current\\Teams.exe"),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), "Programs\\Microsoft VS Code\\Code.exe")
            ]
            
            # Yaygın uygulamaları ekle
            for path in common_paths:
                if os.path.exists(path):
                    exe_name = os.path.basename(path).lower()
                    name = os.path.splitext(exe_name)[0].title()
                    self.discovered_apps[exe_name] = ApplicationInfo(
                        name=name,
                        exe_name=exe_name,
                        path=path,
                        is_running=self._is_process_running(exe_name),
                        description=self._get_file_description(path)
                    )
            
            # Start Menu'den sadece popüler uygulamaları tara
            start_menu_paths = [
                os.path.join(os.environ['APPDATA'], "Microsoft\\Windows\\Start Menu\\Programs"),
                os.path.join(os.environ['PROGRAMDATA'], "Microsoft\\Windows\\Start Menu\\Programs")
            ]
            
            popular_keywords = [
                'chrome', 'firefox', 'edge', 'word', 'excel', 'powerpoint',
                'outlook', 'spotify', 'steam', 'discord', 'teams', 'code',
                'visual studio', 'notepad', 'paint', 'calculator'
            ]
            
            for start_menu in start_menu_paths:
                if os.path.exists(start_menu):
                    for root, _, files in os.walk(start_menu):
                        for file in files:
                            if file.endswith('.lnk'):
                                # Sadece popüler uygulamaları kontrol et
                                if any(keyword in file.lower() for keyword in popular_keywords):
                                    try:
                                        import win32com.client
                                        shell = win32com.client.Dispatch("WScript.Shell")
                                        shortcut = shell.CreateShortCut(os.path.join(root, file))
                                        target_path = shortcut.Targetpath
                                        
                                        if target_path and os.path.exists(target_path) and target_path.lower().endswith('.exe'):
                                            exe_name = os.path.basename(target_path).lower()
                                            if exe_name not in self.discovered_apps:
                                                name = os.path.splitext(file)[0]
                                                self.discovered_apps[exe_name] = ApplicationInfo(
                                                    name=name,
                                                    exe_name=exe_name,
                                                    path=target_path,
                                                    is_running=self._is_process_running(exe_name),
                                                    description=self._get_file_description(target_path)
                                                )
                                    except Exception as e:
                                        self.logger.warning(f"Error processing shortcut {file}: {e}")
            
            self.logger.info(f"Discovered {len(self.discovered_apps)} applications")
            
        except Exception as e:
            self.logger.error(f"Error scanning for applications: {e}")
    
    def _is_process_running(self, exe_name: str) -> bool:
        """Belirtilen uygulamanın çalışıp çalışmadığını kontrol et"""
        try:
            exe_name = exe_name.lower()
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == exe_name:
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking process status: {e}")
            return False
    
    def _get_file_description(self, file_path: str) -> str:
        """Dosya açıklamasını al"""
        try:
            import win32api
            info = win32api.GetFileVersionInfo(file_path, '\\')
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
            
            # Dosya açıklamasını al
            try:
                lang, codepage = win32api.GetFileVersionInfo(file_path, '\\VarFileInfo\\Translation')[0]
                string_file_info = f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\FileDescription'
                description = win32api.GetFileVersionInfo(file_path, string_file_info)
                return f"{description} (v{version})"
            except:
                return f"Version {version}"
        except:
            return ""
    
    def get_running_applications(self) -> List[ApplicationInfo]:
        """Çalışan uygulamaları listele"""
        running_apps = []
        for app_info in self.discovered_apps.values():
            if self._is_process_running(app_info.exe_name):
                app_info.is_running = True
                running_apps.append(app_info)
            else:
                app_info.is_running = False
        return running_apps
    
    def get_available_applications(self) -> List[ApplicationInfo]:
        """Kullanılabilir tüm uygulamaları listele"""
        return list(self.discovered_apps.values())
    
    def launch_application(self, app_name: str) -> bool:
        """Launch an application by name"""
        try:
            app_name = app_name.lower()
            
            # Special launch commands for specific applications
            special_launch = {
                "discord": lambda path: subprocess.Popen([path, "--processStart", "Discord.exe"]),
                "steam": lambda path: subprocess.Popen([path, "-silent"]),
                "opera": lambda path: subprocess.Popen([path, "--disable-update"]),
            }
            
            # System apps direct launch
            system_apps = {
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "notepad": "notepad.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe",
                "explorer": "explorer.exe",
                "taskmgr": "taskmgr.exe",
                "control": "control.exe"
            }
            
            # If it's a system app, try to launch directly first
            if app_name in system_apps:
                try:
                    subprocess.Popen([system_apps[app_name]])
                    self.logger.info(f"Successfully launched system app {app_name}")
                    return True
                except Exception as e:
                    self.logger.error(f"Error launching system app {app_name} directly: {e}")
                    # Continue to normal path search if direct launch fails
            
            # Try to find the application path
            app_path = self._find_application_path(app_name)
            
            # If found, launch the application
            if app_path and os.path.exists(app_path):
                if app_name in special_launch:
                    special_launch[app_name](app_path)
                else:
                    subprocess.Popen([app_path])
                    
                self.logger.info(f"Successfully launched {app_name} from {app_path}")
                return True
            else:
                self.logger.warning(f"Application {app_name} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching application {app_name}: {e}")
            return False
    
    def terminate_application(self, exe_name: str) -> bool:
        """Uygulamayı sonlandır"""
        try:
            exe_name = exe_name.lower()
            if exe_name in self.discovered_apps:
                app_info = self.discovered_apps[exe_name]
                if app_info.is_running:
                    # Önce process'i bul
                    for proc in psutil.process_iter(['name']):
                        if proc.info['name'].lower() == exe_name:
                            proc.terminate()
                            app_info.is_running = False
                            if exe_name in self.running_apps:
                                del self.running_apps[exe_name]
                            return True
            return False
        except Exception as e:
            self.logger.error(f"Error terminating application {exe_name}: {e}")
            return False
    
    def refresh_application_list(self):
        """Uygulama listesini yenile"""
        self._scan_for_applications()

    def _load_app_paths(self) -> dict:
        """Load application paths from config file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('applications', {})
            return {}
        except Exception as e:
            self.logger.error(f"Error loading app paths: {e}")
            return {}

    def _load_music_paths(self) -> dict:
        """Load music paths from config file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('music_directories', [])
            return []
        except Exception as e:
            self.logger.error(f"Error loading music paths: {e}")
            return []

    def _find_application_path(self, app_name: str) -> Optional[str]:
        """Find the path of an application by searching common locations"""
        try:
            # Convert app name to lowercase for comparison
            app_name = app_name.lower()
            
            # System application mappings
            system_apps = {
                "calculator": "calc.exe",
                "notepad": "notepad.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe",
                "explorer": "explorer.exe",
                "taskmgr": "taskmgr.exe",
                "control": "control.exe"
            }
            
            # If it's a system app, convert to correct exe name
            if app_name in system_apps:
                app_name = system_apps[app_name]
            
            # Common program paths for specific applications
            specific_paths = {
                "discord": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Discord", "Update.exe"),
                    os.path.join(os.environ.get('APPDATA', ''), "Discord", "Update.exe")
                ],
                "steam": [
                    "C:\\Program Files (x86)\\Steam\\steam.exe",
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Steam", "steam.exe")
                ],
                "opera": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Programs", "Opera", "launcher.exe"),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Programs", "Opera GX", "launcher.exe")
                ],
                "spotify": [
                    os.path.join(os.environ.get('APPDATA', ''), "Spotify", "Spotify.exe")
                ],
                "telegram": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Telegram Desktop", "Telegram.exe")
                ],
                "whatsapp": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "WhatsApp", "WhatsApp.exe")
                ]
            }
            
            # First check if it's a system app in System32
            if app_name in ["calc.exe", "notepad.exe", "mspaint.exe", "cmd.exe", "taskmgr.exe", "control.exe"]:
                system32_path = os.path.join(os.environ.get('WINDIR', ''), 'System32', app_name)
                if os.path.exists(system32_path):
                    return system32_path
            
            # Then check specific paths
            if app_name.replace('.exe', '') in specific_paths:
                for path in specific_paths[app_name.replace('.exe', '')]:
                    if os.path.exists(path):
                        return path
            
            # Common locations to search
            search_locations = [
                os.environ.get('PROGRAMFILES', ''),
                os.environ.get('PROGRAMFILES(X86)', ''),
                os.environ.get('LOCALAPPDATA', ''),
                os.environ.get('APPDATA', ''),
                r"C:\Windows",
                r"C:\Windows\System32"
            ]
            
            # If it's a .exe file, use it as is, otherwise append .exe
            search_name = app_name if app_name.endswith('.exe') else f"{app_name}.exe"
            
            # Search in common locations
            for location in search_locations:
                if not location:
                    continue
                    
                # First try direct path
                direct_path = os.path.join(location, search_name)
                if os.path.exists(direct_path):
                    return direct_path
                    
                # Then search in subdirectories
                for root, dirs, files in os.walk(location):
                    if search_name.lower() in (f.lower() for f in files):
                        return os.path.join(root, search_name)
                        
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding application path: {e}")
            return None

    def _find_music_file(self, music_name: str) -> Optional[str]:
        """Find a music file in configured music directories"""
        try:
            for music_dir in self.music_paths:
                if os.path.exists(music_dir):
                    for root, _, files in os.walk(music_dir):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                                if music_name.lower() in file.lower():
                                    return os.path.join(root, file)
            return None
        except Exception as e:
            self.logger.error(f"Error searching for music file: {e}")
            return None

    def play_music(self, music_name: str) -> bool:
        """Play a specified music file"""
        try:
            music_path = self._find_music_file(music_name)
            if music_path and os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play()
                self.logger.info(f"Playing music: {music_name}")
                return True
            else:
                self.logger.warning(f"Could not find music file: {music_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error playing music {music_name}: {e}")
            return False

    def stop_music(self):
        """Stop currently playing music"""
        try:
            pygame.mixer.music.stop()
            self.logger.info("Stopped music playback")
        except Exception as e:
            self.logger.error(f"Error stopping music: {e}")

    def update_paths(self, app_paths: dict = None, music_paths: list = None):
        """Update application and music paths in config"""
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            if app_paths is not None:
                config['applications'] = app_paths
                self.app_paths = app_paths

            if music_paths is not None:
                config['music_directories'] = music_paths
                self.music_paths = music_paths

            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            self.logger.info("Successfully updated system paths")
            return True
        except Exception as e:
            self.logger.error(f"Error updating paths: {e}")
            return False 