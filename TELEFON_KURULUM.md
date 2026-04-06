# 📱 Telefondan Telegram Bot Kurulumu

## Gerekenler
- Telegram hesabı ✅ (Var)
- GitHub hesabı (ücretsiz)
-ve-
- **Seçenek A**: Replit.com (en kolay)
- **Seçenek B**: Railway.app (ücretsiz 24/7)

---

## 🎯 SEÇENEK A: REPLIT (Önerilen)

### Adım 1: GitHub'a Yükle

1. **GitHub** hesabı oluşturun: [github.com](https://github.com)
2. **Yeni Repository** oluşturun: "telegram-stock-bot"
3. Telefondan dosya yüklemek için:
   - GitHub Desktop yok, **GitHub.com**'a gidin
   - Repository'ye girin
   - "Add file" → "Upload files"
   - Aşağıdaki dosyaları yükleyin:
     - `telegram_bot.py`
     - `stock_analyzer.py`
     - `stock_screener.py`
     - `requirements.txt`
     - `run_bot.py`
     - `.env`

### Adım 2: Replit'e Bağla

1. **[replit.com](https://replit.com)** açın
2. "Sign up with GitHub" seçin
3. Repository'nizi import edin
4. **Secrets** kısmına token'ı ekleyin:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: `8680064411:AAHFpjkU6Dvr4rZNXAzaoyr21ujmtXzb490`
5. "Run" butonuna basın
6. ✅ Bot çalışıyor!

---

## 🎯 SEÇENEK B: RAILWAY (Ücretsiz 24/7)

### Adım 1: GitHub Yükleme (Yukarıdaki gibi)

### Adım 2: Railway'e Deploy

1. **[railway.app](https://railway.app)** açın
2. "Login with GitHub" seçin
3. "New Project" → "Deploy from GitHub"
4. Repository'nizi seçin
5. **Environment Variables** ekleyin:
   - `TELEGRAM_BOT_TOKEN` = `8680064411:AAHFpjkU6Dvr4rZNXAzaoyr21ujmtXzb490`
6. Deploy butonuna basın
7. ✅ Bot 24/7 çalışıyor!

---

## 📁 Yüklenecek Dosyalar Listesi

```
telegram_bot.py      ← Ana bot kodu
stock_analyzer.py    ← Teknik analiz
stock_screener.py    ← Hisse tarama
requirements.txt     ← Bağımlılıklar
run_bot.py          ← Başlatma scripti
.env                ← Token (sadece sizde kalsın!)
```

---

## ✅ Bot'u Test Etme

1. Telegram'ı açın
2. **@HisseAnalist_123bot** arayın
3. **Start** basın
4. Komut yazın:
   ```
   /start
   ```
5. ✅ Hoş geldiniz mesajı!

---

## 💡 Sonraki Adımlar

Bot çalıştıktan sonra:
1. `/fiyat THYAO` → THYAO fiyatı
2. `/analiz GARAN` → GARAN analizi
3. `/yuklenenler` → Yükseliş hisseleri

---

## ⚠️ Önemli Not

**.env dosyasındaki token'ı asla kimseyle paylaşmayın!**
Token ile bot kontrol edilebilir.
