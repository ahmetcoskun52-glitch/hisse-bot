# Telegram Trading Bot Entegrasyonu - Kurulum ve Kullanım

Hisse alım satım uygulamanız için etkileşimli Telegram chatbot sistemi.

## 📱 Bot Özellikleri

- **Fiyat Sorgulama**: Anlık hisse fiyatı
- **Teknik Analiz**: Destek/Direnç seviyeleri ve trend analizi
- **Yükseliş Tarama**: Potansiyel yükseliş hisseleri taraması
- **Fiyat Uyarıları**: Belirli fiyata ulaşınca bildirim
- **Fiyat Geçmişi**: 30 günlük fiyat değişimleri

## 🚀 Kurulum

### 1. Telegram Bot Oluşturma

1. Telegram'da **@BotFather** kullanıcısını bulun
2. `/newbot` komutunu gönderin
3. Bot ismi belirleyin (örn: "Hisse Analist")
4. BotFather size bir **token** verecek (şuna benzer: `123456789:ABCdefGHI...`)
5. Token'i **kaydedin** (güvenli bir yerde)

### 2. Kurulum

```bash
# Projeyi indirin
cd telegram-trading-bot

# Bağımlılıkları kurun
pip install -r requirements.txt

# Environment dosyası oluşturun
cp .env.example .env

# .env dosyasını düzenleyin
nano .env
```

### 3. Yapılandırma

`.env` dosyasını açın ve token'ınızı girin:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 4. Bot'u Başlatma

```bash
python run_bot.py
```

Veya doğrudan:

```bash
python telegram_bot.py
```

Bot çalıştığında şunu göreceksiniz:
```
✅ Bot hazır! Ctrl+C ile durdurun.
```

## 📖 Komutlar

| Komut | Açıklama |
|-------|----------|
| `/start` | Bot'u başlatır |
| `/yardim` | Komutlar listesini gösterir |
| `/fiyat THYAO` | Anlık fiyat sorgulama |
| `/analiz GARAN` | Destek/Direnç + Trend analizi |
| `/yuklenenler` | Yükseliş potansiyeli hisseler (12 saat) |
| `/uyari THYAO 185.50` | Fiyat uyarısı ekle |
| `/uyarilarim` | Kayıtlı uyarıları göster |
| `/gecmis THYAO` | Son 30 günlük fiyat geçmişi |

## 💬 Kullanım Örnekleri

### Fiyat Sorgulama
```
Kullanıcı: /fiyat THYAO
Bot: 💰 THYAO Fiyat Bilgisi
     📍 BIST:THYAO
     💵 Güncel: 182.50 TL
     🟢 Değişim: +3.25%
     📊 Hacim: 15,234,567
```

### Teknik Analiz
```
Kullanıcı: /analiz THYAO
Bot: 📈 BIST:THYAO Analizi
     💰 Fiyat: 182.50 TL
     🟢 Trend: BULLISH (75% güç)

     🟢 Destek Seviyeleri:
       └ 175.00 TL ████████░░ (5x test)
       └ 170.50 TL ██████░░░░░ (3x test)

     🔴 Direnç Seviyeleri:
       └ 190.00 TL █████████░ (6x test)
       └ 195.00 TL ██████░░░░░ (3x test)
```

### Yükselen Hisseler
```
Kullanıcı: /yuklenenler
Bot: 📈 Yükseliş Potansiyeli Olan Hisseler
     1. 🟢 SASA
        └ 68.40 TL (+5.30%)
        └ Skor: ████████░░ (82/100)
```

### Fiyat Uyarısı
```
Kullanıcı: /uyari THYAO 185.50
Bot: ✅ Uyarı Eklendi!
     📌 Sembol: THYAO
     🎯 Hedef Fiyat: 185.50 TL
```

## 🔧 Mevcut Projeye Entegrasyon

### Yeni Dosyalar

Projenize kopyalamanız gereken dosyalar:
- `telegram_bot.py` - Ana bot kodu
- `stock_analyzer.py` - Teknik analiz modülü
- `stock_screener.py` - Hisse tarama modülü

### Kullanım

```python
from telegram_bot import run_bot

# Token ile çalıştır
run_bot("your_bot_token_here")
```

### Kendi Fiyat API'nizi Entegre Etme

`telegram_bot.py` dosyasında bu fonksiyonları düzenleyin:

```python
def get_demo_price_data(symbol: str):
    # Buraya kendi API'nizi ekleyin
    # Örnek: return your_api.get_stock_price(symbol)
    pass

def get_price_history(symbol: str, days: int = 30):
    # Buraya kendi API'nizi ekleyin
    # Örnek: return your_api.get_price_history(symbol, days)
    pass
```

## 📊 Teknik Analiz Detayları

### Destek/Direnç Bulma
- **Pencereli Ekstremum Algoritması**: Local minima/maxima tespiti
- **Güç Hesaplama**: Seviyenin kaç kez test edildiğine göre (2+ dokunuş)
- **Yakınlık Birleştirme**: %2 tolerans ile benzer seviyeleri birleştirir

### Trend Analizi
- **Hareketli Ortalamalar**: 10 ve 30 günlük MA karşılaştırması
- **RSI (Relative Strength Index)**: 14 periyot RSI hesaplaması
- **Momentum**: Son 10 günlük fiyat değişimi

### Yükseliş Tarama Kriterleri
- Fiyat momentum skoru (30 puan)
- Hacim artış oranı (25 puan)
- Momentum tutarlılığı (25 puan)
- Trend tutarlılığı (20 puan)
- Minimum hacim: 1,000,000 lot

## ⚠️ Önemli Notlar

1. **Demo Veri**: Şu an demo veriler kullanılıyor. Gerçek hisse verileri için API entegrasyonu yapın.

2. **Rate Limiting**: Telegram API sınırlamalarına dikkat edin. Yoğun kullanımda 429 hatası alabilirsiniz.

3. **Güvenlik**: Token'ınızı .env dosyasında saklayın, asla kodda sabit tutmayın.

4. **Yaygın Hatalar**:
   - `Chat not found`: Chat ID hatalı
   - `Bot was blocked`: Kullanıcı botu engellemiş
   - `Unauthorized`: Token hatalı

## 🔌 API Entegrasyonu

Gerçek Borsa verisi için önerilen API'ler:

### 🇹🇷 BIST için
- [ investing.com API](https://www.investing.com/api/)
- [ Yahoo Finance](https://finance.yahoo.com/)
- [ Matriks](https://www.matriksdata.com/)
- [ Foreks](https://www.foreks.com/)

### Global
- [Alpha Vantage](https://www.alphavantage.co/)
- [Polygon.io](https://polygon.io/)
- [IEX Cloud](https://iexcloud.io/)

Örnek API entegrasyonu:

```python
import yfinance as yf

def get_real_price(symbol: str) -> dict:
    ticker = yf.Ticker(f"{symbol}.IS")
    data = ticker.history(period="1d")
    return {
        "price": data['Close'].iloc[-1],
        "change": ((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
    }
```

## 📁 Dosya Yapısı

```
├── telegram_bot.py      # Ana bot kodu
├── stock_analyzer.py    # Teknik analiz modülü
├── stock_screener.py    # Hisse tarama modülü
├── run_bot.py           # Başlatma scripti
├── config.py            # Yapılandırma
├── requirements.txt     # Bağımlılıklar
├── .env.example         # Environment şablonu
└── README.md            # Bu dosya
```

## 🆘 Sorun Giderme

### Bot yanıt vermiyor
1. Token doğru mu kontrol edin
2. Bot'un çalıştığını doğrulayın
3. Internet bağlantısını kontrol edin

### "Invalid token" hatası
- Token formatını kontrol edin
- BotFather'dan yeni token alın

### Veri hatalı
- Demo modda çalışıyor olabilir
- API entegrasyonu yapın

## 📄 Lisans

MIT License - Dilediğiniz gibi kullanın ve geliştirin.
