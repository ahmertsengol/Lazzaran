# 🎙️ Lazzaran - Türkçe Sesli Asistan

<div align="center">

![Lazzaran Logo](assets/logo.jpg)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/version-1.1.0-green.svg)](https://github.com/ahmertsengol/Lazzaran/releases)

*Lazzaran, yapay zeka destekli Türkçe sesli komutları anlayabilen, modern ve kullanıcı dostu bir masaüstü asistanıdır.*

[Özellikler](#özellikler) • [Kurulum](#kurulum) • [Kullanım](#kullanım) • [Geliştirme](#geliştirme) • [Katkıda Bulunma](#katkıda-bulunma) • [İletişim](#i̇letişim)

</div>

---

## 📋 İçindekiler
- [Özellikler](#özellikler)
- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Geliştirme](#geliştirme)
- [SSS](#sss)
- [Yol Haritası](#yol-haritası)
- [Katkıda Bulunma](#katkıda-bulunma)
- [Lisans](#lisans)

## ✨ Özellikler

### 🖥️ Uygulama Kontrolü
#### Sistem Uygulamaları
- **Temel Uygulamalar**
  - 🧮 Hesap Makinesi (`hesap makinesini aç`, `hesaplayıcı başlat`)
  - 📝 Not Defteri (`not defterini aç`, `notepad başlat`)
  - 🎨 Paint (`paint aç`, `resim programını başlat`)
  - 📊 Görev Yöneticisi (`görev yöneticisini aç`)
  - 📂 Dosya Gezgini (`dosya gezginini aç`)
  - ⚙️ Denetim Masası (`denetim masasını aç`)

#### Popüler Uygulamalar
- **Web Tarayıcıları**
  - 🌐 Google Chrome (`chrome'u aç`, `tarayıcıyı başlat`)
  - 🦊 Mozilla Firefox (`firefox'u aç`)
  - 🔴 Opera (`opera'yı aç`)
  - 💠 Microsoft Edge (`edge'i aç`)

- **Ofis Uygulamaları**
  - 📘 Microsoft Word (`word'ü aç`, `kelime işlemciyi başlat`)
  - 📊 Microsoft Excel (`excel'i aç`, `hesap tablosunu başlat`)
  - 📑 Microsoft PowerPoint (`powerpoint'i aç`, `sunu programını başlat`)

- **İletişim ve Medya**
  - 💬 Discord (`discord'u aç`)
  - 🎵 Spotify (`spotify'ı aç`, `müzik aç`)
  - 👥 Teams (`teams'i aç`)
  - ✈️ Telegram (`telegram'ı aç`)
  - 📱 WhatsApp (`whatsapp'ı aç`)

- **Oyun ve Eğlence**
  - 🎮 Steam (`steam'i aç`)
  - 🎯 Epic Games (`epic'i aç`)

### 🌐 Web Servisleri
- 🎥 YouTube açma ve video arama
- 🔍 Google açma ve arama yapma
- ⛅ Hava durumu sorgulama
- 📰 Güncel haberleri getirme
- 🕒 Saat bilgisi

### ⚡ Sistem Komutları
- 💻 Bilgisayarı kapatma
- 🔄 Bilgisayarı yeniden başlatma
- 📋 Çalışan uygulamaları listeleme
- ❌ Uygulamaları kapatma

## 💻 Sistem Gereksinimleri

- **İşletim Sistemi:** Windows 10/11
- **Python Sürümü:** 3.8 veya üzeri
- **RAM:** Minimum 4GB (8GB önerilen)
- **Depolama:** 500MB boş alan
- **Donanım:** 
  - Mikrofon (ses girişi için)
  - Hoparlör (ses çıkışı için)
- **İnternet:** Sürekli bağlantı

## 🚀 Kurulum

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/ahmertsengol/Lazzaran.git
cd Lazzaran
```

### 2. Sanal Ortam Oluşturun (Önerilen)
```bash
python -m venv venv
# Windows için
venv\Scripts\activate
# Linux/Mac için
source venv/bin/activate
```

### 3. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarlayın
`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli API anahtarlarını ekleyin:
```env
WEATHER_API_KEY=your_api_key
NEWS_API_KEY=your_api_key
GEMINI_API_KEY=your_api_key
```

### 5. Uygulamayı Başlatın
```bash
python main.py
```

## 📖 Kullanım

### Temel Komutlar
```plaintext
👋 "Merhaba Lazzaran" - Asistanı aktifleştir
🖥️ "[Uygulama adı] aç" - Uygulama başlat
🌤️ "Hava durumu nasıl?" - Hava durumu bilgisi
📰 "Haberleri göster" - Güncel haberler
⏰ "Saat kaç?" - Güncel saat
```

### Gelişmiş Özellikler
- **Akıllı Uygulama Tanıma:** Farklı komut varyasyonlarını anlama
- **Özel Başlatma Parametreleri:** Discord, Steam gibi uygulamalar için
- **Hata Toleransı:** Yanlış telaffuzları düzeltme
- **Bağlam Anlama:** Karmaşık komutları yorumlama

## 🛠️ Geliştirme

### Proje Yapısı
```
lazzaran/
├── core/               # Çekirdek modüller
├── services/          # Harici servis entegrasyonları
├── ui/                # Kullanıcı arayüzü bileşenleri
├── config/            # Yapılandırma dosyaları
├── tests/             # Test dosyaları
└── docs/              # Dokümantasyon
```

### Test
```bash
pytest tests/
```

## ❓ SSS

<details>
<summary>Hangi dilleri destekliyor?</summary>
Şu an sadece Türkçe desteklenmektedir. Diğer diller için geliştirme devam etmektedir.
</details>

<details>
<summary>API anahtarlarını nereden alabilirim?</summary>
Gerekli API anahtarları için dokümantasyonun API Anahtarları bölümüne bakın.
</details>

## 🗺️ Yol Haritası

- [ ] Çoklu dil desteği
- [ ] Mobil uygulama
- [ ] Takvim entegrasyonu
- [ ] Kişiselleştirilmiş yanıtlar
- [ ] Gelişmiş AI özellikleri

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

Ahmet Şengöl - [@ahmertsengol](https://twitter.com/ahmertsengol) - 21sandn21@gmail.com

Proje Linki: [https://github.com/ahmertsengol/Lazzaran](https://github.com/ahmertsengol/Lazzaran)

---

<div align="center">
Made with ❤️ by <a href="https://github.com/ahmertsengol">Ahmet Mert Şengöl</a>
</div>

