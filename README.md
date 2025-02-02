# 🎙️ Lazzaran Voice Assistant

<div align="center">

![Lazzaran Logo](assets/Logo.jpg)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)

*A modern, intelligent voice assistant built in Python with advanced features and modular architecture*

[Key Features](#-key-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Configuration](#-configuration) •
[Contributing](#-contributing)

</div>

---

## 🌟 Key Features

- 🗣️ **Voice Command Recognition**
  - Natural language processing
  - Multi-language support
  - Noise-resistant recognition

- 🤖 **AI-Powered Conversations**
  - Powered by Google's Gemini AI
  - Context-aware responses
  - Conversation history tracking

- 🌍 **Real-time Information**
  - Weather updates
  - News headlines
  - Time and date information

- 💻 **System Control**
  - Application launching
  - System commands
  - Web browser integration

- 📱 **Modern UI**
  - Dark mode support
  - Real-time status updates
  - Command history display

## 🛠️ Project Structure

```
PyhtonVoiceAssistant/
├── 📁 core/                     # Core functionality
│   ├── 📄 voice_assistant.py    # Voice processing
│   ├── 📄 command_handler.py    # Command processing
│   └── 📁 services/            # Individual services
│       ├── 📄 weather.py       # Weather service
│       ├── 📄 news.py          # News service
│       └── 📄 ai_service.py    # AI conversation service
├── 📁 config/                   # Configuration
├── 📁 ui/                       # User interface
├── 📁 utils/                    # Utility functions
├── 📁 tests/                    # Test suite
├── 📄 .env.example             # Environment variables
├── 📄 requirements.txt         # Dependencies
└── 📄 main.py                  # Entry point
```

## 📥 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/LaZzaran/PythonVoiceAssistant.git
   cd PythonVoiceAssistant
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🎮 Usage

1. **Start the Assistant**
   ```bash
   python main.py
   ```

2. **Available Commands**
   - "Hava durumu" - Get weather information
   - "Haberler" - Get latest news
   - "Saat" - Get current time
   - "Google aç" - Open Google
   - And many more...

## ⚙️ Configuration

The application can be configured through:

1. **Environment Variables** (.env file)
   ```env
   GEMINI_API_KEY=your_key_here
   NEWS_API_KEY=your_key_here
   WEATHER_API_KEY=your_key_here
   ```

2. **Config File** (config.yaml)
   ```yaml
   voice:
     language: tr-TR
     timeout: 5
   ```

3. **Command Line Arguments**
   ```bash
   python main.py --language tr-TR --timeout 5
   ```

## 📸 Screenshots

<div align="center">
<img src="assets/screenshot1.png" width="45%" alt="Main Interface"/>
<img src="assets/screenshot2.png" width="45%" alt="Voice Recognition"/>
</div>

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for conversation capabilities
- OpenWeatherMap for weather data
- NewsAPI for news updates

---

<div align="center">

**Made with ❤️ by LaZzaran**

[⬆ Back to top](#-lazzaran-voice-assistant)

</div>

