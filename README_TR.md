# 📱 Telegram Fiyat Uyarı Bildirim Sistemi

Hisse alım satım uygulamanız için Telegram entegrasyon modülü.

## 🚀 Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Telegram Bot Oluşturma

1. **BotFather'a gidin**: Telegram'da @BotFather kullanıcısını bulun
2. **Yeni bot oluşturun**: `/newbot` komutunu gönderin
3. **Token alın**: BotFather size bir API token verecek
4. **Token'i kaydedin**: Token'i güvenli bir yerde saklayın

### Chat ID Alma

1. **@userinfobot kullanın**: Telegram'da @userinfobot'a mesaj gönderin
2. **Chat ID'yi alın**: Size bir ID numarası verecek
3. **Alternatif**: Telegram API'yi kullanarak `getUpdates` metodunu çağırın

## 📁 Dosya Yapısı

```
├── telegram_notifier.py   # Ana bildirim modülü
├── config.py              # Yapılandırma ayarları
├── example_usage.py       # Entegrasyon örnekleri
├── requirements.txt       # Python bağımlılıkları
├── .env.example          # Ortam değişkenleri şablonu
└── README_TR.md          # Bu dosya
```

## ⚡ Hızlı Başlangıç

### 1. Yapılandırma

`.env` dosyası oluşturun:
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 2. Basit Kullanım

```python
from telegram_notifier import TelegramNotifier

# Notifier oluştur
notifier = TelegramNotifier(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

# Fiyat uyarısı gönder
notifier.send_price_alert(
    symbol="THYAO",
    current_price=185.50,
    target_price=185.00,
    alert_type="above"
)
```

### 3. Uyarı Yönetimi

```python
from telegram_notifier import TelegramNotifier, PriceAlertManager

notifier = TelegramNotifier(bot_token="...", chat_id="...")
alert_manager = PriceAlertManager(notifier)

# Uyarı ekle
alert_manager.add_alert("THYAO", target_price=190.00, alert_type="above")

# Fiyat kontrolü
alert_manager.check_alerts("THYAO", current_price=191.00)
```

### 4. İşlem Bildirimleri

```python
# Alım bildirimi
notifier.send_trade_notification(
    symbol="THYAO",
    action="BUY",
    quantity=100,
    price=180.00,
    total_value=18000.00
)

# Satış bildirimi
notifier.send_trade_notification(
    symbol="THYAO",
    action="SELL",
    quantity=100,
    price=185.00,
    total_value=18500.00
)
```

### 5. Portföy Özeti

```python
notifier.send_portfolio_update(
    total_value=150000.00,
    daily_change=2500.00,
    daily_change_percent=1.69,
    top_gainers=[
        {"symbol": "THYAO", "change": 3.25},
        {"symbol": "ASELS", "change": 2.10}
    ],
    top_losers=[
        {"symbol": "EREGL", "change": -1.50}
    ]
)
```

## 📊 Bildirim Türleri

### Fiyat Uyarıları
- `above`: Fiyat belirli seviyeyi aştığında
- `below`: Fiyat belirli seviyenin altına düştüğünde
- `percent_change`: Yüzde değişim bildirimi
- `volume_spike`: Hacim artışı bildirimi

### İşlem Bildirimleri
- Alım/Satım gerçekleştiğinde
- İşlem detayları (sembol, adet, fiyat, toplam)

### Portföy Bildirimleri
- Günlük özet
- En çok kazanan/kaybedenler
- Toplam değer değişimi

## 🔧 Mevcut Projeye Entegrasyon

### Adım 1: Dosyaları Kopyalayın
`telegram_notifier.py` ve `config.py` dosyalarını projenize kopyalayın.

### Adım 2: Yapılandırmayı Ayarlayın
Ortam değişkenlerini ayarlayın veya `config.py` içinde yapılandırın.

### Adım 3: Entegrasyon

```python
# Mevcut kodunuzun başına ekleyin
from telegram_notifier import TelegramNotifier, PriceAlertManager
from config import load_config

# Yapılandırma
telegram_config, _, _ = load_config()

# Notifier
notifier = TelegramNotifier(
    bot_token=telegram_config.bot_token,
    chat_id=telegram_config.chat_id
)

# Fiyat kontrolü sonrası
notifier.send_price_alert(
    symbol=hisse_symbol,
    current_price=mevcut_fiyat,
    target_price=hedef_fiyat,
    alert_type="above"
)
```

## ⚠️ Önemli Notlar

1. **Güvenlik**: Bot token'ınızı asla paylaşmayın veya kodda sabit tutmayın
2. **Rate Limiting**: Telegram API sınırlamalarına dikkat edin
3. **Test**: Canlıya almadan önce test grubunda deneyin
4. **Hata Yönetimi**: Bağlantı hatalarını ele alın

## 🐛 Sorun Giderme

### "Chat not found" Hatası
- Chat ID'nin doğru olduğundan emin olun
- Bot'a mesaj gönderdiğinizden emin olun

### "Bot was blocked by the user"
- Kullanıcı botu engellemiş
- Kullanıcının bot'u başlatmasını bekleyin

### Bağlantı Hatası
- Internet bağlantınızı kontrol edin
- Telegram sunucularının erişilebilir olduğundan emin olun

## 📄 Lisans

Bu proje MIT lisansı altında sunulmaktadır.
