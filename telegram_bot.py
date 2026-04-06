"""
Telegram Trading Bot - Ana Modül
Etkileşimli hisse analiz chatbot'u
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        filters,
        ContextTypes,
        ConversationHandler,
    )
    from telegram.error import TelegramError
except ImportError:
    raise ImportError("python-telegram-bot kütüphanesi kurulu değil. pip install python-telegram-bot")

from stock_analyzer import StockAnalyzer, TrendAnalysis
from stock_screener import StockScreener, ScanResult

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- DURUM SABİTLERİ ---
@dataclass
class UserState:
    """Kullanıcı durumu"""
    selected_stocks: List[str] = field(default_factory=list)
    last_scan_result: Optional[ScanResult] = None
    price_alerts: Dict[str, float] = field(default_factory=dict)
    last_analysis: Optional[TrendAnalysis] = None


# --- KOMUTLAR ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot başlatıldığında çalışır"""
    welcome_message = (
        "📊 <b>Hoş Geldiniz!</b>\n\n"
        "Ben sizin hisse analiz asistanınızım.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 <b>NASIL ÇALIŞIR?</b>\n\n"
        "1️⃣ <code>/baslat_bildirim</code> → Taramayı başlat\n"
        "2️⃣ İzlediğiniz hisseler takip edilir\n"
        "3️⃣ <b>🚀 TÜM PİYASA tarama</b> başlar!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📈 <b>Otomatik Bildirimler:</b>\n\n"
        "🟢 Yükseliş sinyali (izlediğiniz hisseler)\n"
        "🔴 Sinyal iptali (düşüş başladı)\n"
        "🎯 Hedef fiyata ulaştı\n\n"
        "🚀 <b>ANİ YÜKSELİŞ (Tüm Piyasa!)</b>\n"
        "İzleme listenizde OLMASA bile\n"
        "bir hisse +3% üzeri yükselirse\n"
        "<b>→ Anında haber alırsınız!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<i>💡 Hemen /baslat_bildirim yazın!</i>"
    )

    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım komutu"""
    help_text = (
        "📖 <b>Kullanım Kılavuzu</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 <b>Temel Analiz:</b>\n\n"
        "📈 <b>/fiyat THYAO</b>\n"
        "   └ Hisse anlık fiyat bilgisi\n\n"
        "📊 <b>/analiz GARAN</b>\n"
        "   └ Destek/Direnç + Trend analizi\n\n"
        "🚀 <b>/yuklenenler</b>\n"
        "   └ Yükseliş hisseleri + Hedef Fiyatlar\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔔 <b>Otomatik Bildirim (YENİ!):</b>\n\n"
        "👁️ <b>/izle THYAO</b>\n"
        "   └ Hisseyi izlemeye al\n"
        "   └ Yükseliş olunca bildirim gelir!\n\n"
        "🔔 <b>/baslat_bildirim</b>\n"
        "   └ 10 hisseyi otomatik izlemeye al\n"
        "   └ Sinyal değişince bildirim!\n\n"
        "📋 <b>/izlemelerim</b>\n"
        "   └ İzlenen hisseleri göster\n\n"
        "🗑️ <b>/izlemeyi_birak THYAO</b>\n"
        "   └ İzlemeden çıkar\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📜 <b>/gecmis THYAO</b>\n"
        "   └ Son 30 günlük fiyat geçmişi\n\n"
        "💡 <b>İpuçları:</b>\n"
        "• /baslat_bildirim en önemli komut!\n"
        "• Yükseliş sinyali → Otomatik bildirim\n"
        "• Sinyal iptali → Düşüş uyarısı"
    )

    await update.message.reply_text(help_text, parse_mode='HTML')


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fiyat sorgulama komutu"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>Kullanım:</b>\n<code>/fiyat [HİSSE]</code>\n\n"
            "Örnek: <code>/fiyat THYAO</code>",
            parse_mode='HTML'
        )
        return

    symbol = context.args[0].upper()

    # Demo veri - gerçek entegrasyon için API ekleyin
    price_data = get_demo_price_data(symbol)

    if not price_data:
        await update.message.reply_text(
            f"❌ <b>{symbol}</b> sembolü bulunamadı.\n"
            "Lütfen geçerli bir BIST sembolü girin.",
            parse_mode='HTML'
        )
        return

    message = (
        f"💰 <b>{symbol}</b> Fiyat Bilgisi\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 BIST:{symbol}\n"
        f"💵 Güncel: <b>{price_data['price']:,.2f} TL</b>\n"
        f"{price_data['emoji']} Değişim: <b>{price_data['change']:+.2f}%</b>\n"
        f"📊 Hacim: {price_data['volume']:,}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    await update.message.reply_text(message, parse_mode='HTML')


async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Teknik analiz komutu"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>Kullanım:</b>\n<code>/analiz [HİSSE]</code>\n\n"
            "Örnek: <code>/analiz THYAO</code>\n\n"
            "Detaylı analiz için /analiz yerine kullanın.",
            parse_mode='HTML'
        )
        return

    symbol = context.args[0].upper()

    # Analiz yap
    prices = get_price_history(symbol)

    if not prices:
        await update.message.reply_text(
            f"❌ <b>{symbol}</b> için veri bulunamadı.\n"
            "Lütfen geçerli bir BIST sembolü girin.",
            parse_mode='HTML'
        )
        return

    analyzer = StockAnalyzer()
    analysis = analyzer.analyze(prices)
    message = analyzer.format_analysis_message(symbol, analysis)

    await update.message.reply_text(message, parse_mode='HTML')


async def rising_stocks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yükseliş potansiyeli olan hisseler + Hedef fiyatlar"""
    await update.message.reply_text(
        "🔍 <b>Yükseliş potansiyeli taranıyor...</b>\n"
        "📊 Teknik analiz yapılıyor...\n"
        "Lütfen biraz bekleyin... ⏳",
        parse_mode='HTML'
    )

    # Demo veri (gerçek API için değiştirin)
    symbols = ["THYAO", "GARAN", "EREGL", "ASELS", "KCHOL", "TUPRS", "SASA", "PGSUS", "TAVHL", "BIMAS", "SAHOL", "AKBNK"]
    demo_data = generate_demo_data(symbols, days=30)

    # Tarama
    screener = StockScreener()
    result = screener.scan_for_rising_stocks(demo_data, timeframe_hours=12)
    message = screener.format_scan_result(result)

    await update.message.reply_text(message, parse_mode='HTML')


async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fiyat uyarısı ekleme"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ <b>Kullanım:</b>\n<code>/uyari [HİSSE] [FİYAT]</code>\n\n"
            "Örnek: <code>/uyari THYAO 185.50</code>",
            parse_mode='HTML'
        )
        return

    symbol = context.args[0].upper()

    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text(
            "❌ <b>Geçersiz fiyat!</b>\n"
            "Lütfen sayısal bir değer girin.\n"
            "Örnek: <code>/uyari THYAO 185.50</code>",
            parse_mode='HTML'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = UserState()

    user_states[user_id].price_alerts[symbol] = target_price

    await update.message.reply_text(
        f"✅ <b>Uyarı Eklendi!</b>\n\n"
        f"📌 Sembol: <code>{symbol}</code>\n"
        f"🎯 Hedef Fiyat: <b>{target_price:,.2f} TL</b>\n\n"
        f"<i>{symbol} bu fiyata ulaşınca size bildirim gönderilecek.</i>",
        parse_mode='HTML'
    )


async def my_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının uyarılarını göster"""
    user_id = update.effective_user.id

    if user_id not in user_states or not user_states[user_id].price_alerts:
        await update.message.reply_text(
            "📭 <b>Kayıtlı Uyarınız Yok</b>\n\n"
            "<code>/uyari [HİSSE] [FİYAT]</code> ile uyarı ekleyin.\n"
            "Örnek: <code>/uyari THYAO 185.50</code>",
            parse_mode='HTML'
        )
        return

    alerts_text = "🔔 <b>Kayıtlı Uyarılarınız</b>\n━━━━━━━━━━━━━━━━━━━━\n"

    for symbol, price in user_states[user_id].price_alerts.items():
        alerts_text += f"📌 {symbol}: {price:,.2f} TL\n"

    alerts_text += f"\n⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"

    await update.message.reply_text(alerts_text, parse_mode='HTML')


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fiyat geçmişi"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>Kullanım:</b>\n<code>/gecmis [HİSSE]</code>\n\n"
            "Örnek: <code>/gecmis THYAO</code>",
            parse_mode='HTML'
        )
        return

    symbol = context.args[0].upper()
    prices = get_price_history(symbol, days=30)

    if not prices:
        await update.message.reply_text(
            f"❌ <b>{symbol}</b> için veri bulunamadı.",
            parse_mode='HTML'
        )
        return

    # Son 7 günlük değişim
    recent = prices[-7:] if len(prices) >= 7 else prices
    weekly_change = ((recent[-1] - recent[0]) / recent[0]) * 100

    monthly_change = ((prices[-1] - prices[0]) / prices[0]) * 100

    highest = max(prices)
    lowest = min(prices)

    message = (
        f"📜 <b>{symbol}</b> Fiyat Geçmişi\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Son Fiyat:</b> {prices[-1]:,.2f} TL\n\n"
        f"📈 Haftalık Değişim: {weekly_change:+.2f}%\n"
        f"📈 Aylık Değişim: {monthly_change:+.2f}%\n\n"
        f"🔼 En Yüksek (30g): {highest:,.2f} TL\n"
        f"🔽 En Düşük (30g): {lowest:,.2f} TL\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    await update.message.reply_text(message, parse_mode='HTML')


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bilinmeyen mesajları işle"""
    await update.message.reply_text(
        "🤔 Bu komudu tanımadım.\n\n"
        "<code>/yardim</code> yazarak tüm komutları görebilirsiniz.",
        parse_mode='HTML'
    )


async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisseyi izleme listesine ekler"""
    if not context.args:
        # İzleme durumunu göster
        watched = monitor.get_watched_stocks()
        if watched:
            message = "📋 <b>İzlenen Hisseler</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            for s in watched:
                message += f"👁️ {s}\n"
            message += f"\n⏰ Tarama: Her {monitor.scan_interval} saniyede\n"
            message += f"/izle [HİSSE] ile ekle\n/izlemeyi_birak [HİSSE] ile çıkar"
        else:
            message = (
                "📋 <b>İzleme Listesi Boş</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "<code>/izle THYAO</code> yazarak hisse ekleyin.\n"
                "Eklendiğinde otomatik bildirim alırsınız!"
            )
        await update.message.reply_text(message, parse_mode='HTML')
        return

    symbol = context.args[0].upper()
    monitor.add_stock(symbol)

    await update.message.reply_text(
        f"✅ <b>İzleme Eklendi!</b>\n\n"
        f"📌 {symbol} izleme listesine eklendi.\n\n"
        f"📊 Bu hisse için:\n"
        f"   • Yükseliş sinyali → <b>Otomatik bildirim</b>\n"
        f"   • Sinyal iptali → <b>Otomatik bildirim</b>\n"
        f"   • Hedef fiyat → <b>Otomatik bildirim</b>\n\n"
        f"<i>Tarama her {monitor.scan_interval} saniyede yapılıyor.</i>",
        parse_mode='HTML'
    )


async def unwatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisseyi izleme listesinden çıkarır"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>Kullanım:</b>\n<code>/izlemeyi_birak [HİSSE]</code>\n\n"
            "Örnek: <code>/izlemeyi_birak THYAO</code>",
            parse_mode='HTML'
        )
        return

    symbol = context.args[0].upper()
    monitor.remove_stock(symbol)

    await update.message.reply_text(
        f"✅ <b>İzleme Kaldırıldı!</b>\n\n"
        f"📌 {symbol} artık izlenmiyor.",
        parse_mode='HTML'
    )


async def start_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Otomatik bildirimleri başlatır"""
    # Önce tüm BIST hisselerini izle
    symbols = ["THYAO", "GARAN", "EREGL", "ASELS", "KCHOL", "TUPRS", "SASA", "PGSUS", "BIMAS", "SAHOL"]
    for s in symbols:
        monitor.add_stock(s)

    # Piyasa geneli taramayı aktif et
    monitor.set_market_wide_scan(enabled=True, min_rally=3.0)

    await update.message.reply_text(
        f"🔔 <b>Otomatik Bildirimler Aktif!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 İzlenen Hisseler: {len(symbols)}\n"
        f"⏱️ Tarama Aralığı: Her {monitor.scan_interval} saniye\n\n"
        f"<b>Bildirim Alacağınız Durumlar:</b>\n\n"
        f"<b>📋 İZLEDİĞİNİZ HİSSELER:</b>\n"
        f"🟢 Hisse yükseliş sinyali verdi\n"
        f"🔴 Yükseliş sinyali iptal oldu\n"
        f"🎯 Hedef fiyata ulaştı\n\n"
        f"<b>🚀 DİKKAT! TÜM PİYASA:</b>\n"
        f"⚡ <b>Yeni yükseliş tespit edildiğinde\n"
        f"izleme listenizde OLMASA bile!</b>\n"
        f"🚀 Ani yükseliş bildirimi gelir!\n\n"
        f"<i>• Bir hisse ani yükseliş yapınca\n"
        f"• +3% ve üzeri fiyat artışı olunca\n"
        f"• Hacim 2x ve üzeri artınca\n"
        f"→ Anında haber alırsınız!</i>",
        parse_mode='HTML'
    )


async def my_watches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İzlenen hisselerin durumunu gösterir"""
    watched = monitor.get_watched_stocks()

    if not watched:
        await update.message.reply_text(
            "📋 <b>İzleme Listesi Boş</b>\n\n"
            "<code>/izle THYAO</code> ile hisse ekleyin.\n"
            "<code>/baslat_bildirim</code> ile otomatik taramayı başlatın.",
            parse_mode='HTML'
        )
        return

    message = "📋 <b>İzlenen Hisselerin Durumu</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"

    # Demo veri ile durumları göster
    demo_data = generate_demo_data(watched, days=30)
    from stock_screener import StockScreener

    screener = StockScreener()
    for symbol in watched[:10]:
        if symbol in demo_data:
            prices, volumes = demo_data[symbol]
            rec = screener.analyze_stock(symbol, prices, volumes)
            if rec:
                emoji = "🟢" if "bullish" in rec.trend else ("🔴" if "bearish" in rec.trend else "🟡")
                message += f"{emoji} {symbol}: Skor {rec.score:.0f}/100\n"

    message += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    message += f"Toplam: {len(watched)} hisse izleniyor\n"
    message += f"⏱️ Tarama: Her {monitor.config.scan_interval}s"

    await update.message.reply_text(message, parse_mode='HTML')


async def set_frequency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bildirim sıklığını ayarlar"""
    if not context.args:
        current = monitor.config.scan_interval
        await update.message.reply_text(
            f"⚙️ <b>Bildirim Sıklığı</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Mevcut: <b>Her {current} saniye</b>\n\n"
            f"📝 Değiştirmek için:\n"
            f"<code>/sıklık 15</code> = Her 15 saniye (ÇOK SIK)\n"
            f"<code>/sıklık 30</code> = Her 30 saniye (SIK)\n"
            f"<code>/sıklık 60</code> = Her 1 dakika (NORMAL)\n"
            f"<code>/sıklık 120</code> = Her 2 dakika (AYAZ)\n\n"
            f"⚠️ <b>Ne kadar sık olursa:</b>\n"
            f"• Daha fazla bildirim\n"
            f"• Daha hızlı tespit\n"
            f"• Daha çok RAM/CPU kullanımı\n\n"
            f"💡 <b>Önerilen:</b> 30 saniye",
            parse_mode='HTML'
        )
        return

    try:
        seconds = int(context.args[0])
        if seconds < 15:
            seconds = 15  # Minimum 15 saniye
        if seconds > 300:
            seconds = 300  # Maximum 5 dakika

        monitor.set_notification_frequency(seconds)

        await update.message.reply_text(
            f"✅ <b>Sıklık Güncellendi!</b>\n\n"
            f"📊 Yeni tarama aralığı: <b>Her {seconds} saniye</b>\n\n"
            f"⏱️ Değişiklik aktif hemen uygulanır.",
            parse_mode='HTML'
        )

    except ValueError:
        await update.message.reply_text(
            "❌ <b>Geçersiz değer!</b>\n\n"
            "Örnek: <code>/sıklık 30</code>",
            parse_mode='HTML'
        )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sistem durumunu gösterir"""
    status = monitor.get_status()

    await update.message.reply_text(status, parse_mode='HTML')


# --- YARDIMCI FONKSİYONLAR ---
def get_demo_price_data(symbol: str) -> Optional[Dict]:
    """Demo için fiyat verisi döndürür"""
    import random
    random.seed(hash(symbol) % 1000)

    demo_prices = {
        "THYAO": (182.50, 3.25),
        "GARAN": (48.75, 1.85),
        "EREGL": (36.20, -0.85),
        "ASELS": (52.30, 4.10),
        "KCHOL": (128.00, 2.45),
        "TUPRS": (145.80, -1.20),
        "SASA": (68.40, 5.30),
        "PGSUS": (240.00, 2.80),
        "TAVHL": (180.50, 0.95),
        "BIMAS": (420.00, 1.15),
    }

    if symbol in demo_prices:
        price, change = demo_prices[symbol]
        return {
            "price": price,
            "change": change,
            "volume": random.randint(5000000, 50000000),
            "emoji": "🟢" if change > 0 else "🔴"
        }

    return None


def get_price_history(symbol: str, days: int = 30) -> List[float]:
    """Demo için fiyat geçmişi oluşturur"""
    import random
    random.seed(hash(symbol) % 1000)

    # Başlangıç fiyatı
    base_prices = {
        "THYAO": 165, "GARAN": 45, "EREGL": 34, "ASELS": 48,
        "KCHOL": 120, "TUPRS": 140, "SASA": 62, "PGSUS": 220,
        "TAVHL": 170, "BIMAS": 400,
    }

    start_price = base_prices.get(symbol, 100)

    # Fiyat serisi oluştur
    prices = [start_price]
    for i in range(days):
        # Rastgele yürüyüş
        change = random.uniform(-2.5, 3)
        prices.append(prices[-1] * (1 + change / 100))

    return prices


def generate_demo_data(symbols: List[str], days: int = 30) -> Dict[str, tuple]:
    """Demo veri üretir"""
    import random
    data = {}

    for symbol in symbols:
        random.seed(hash(symbol) % 1000)
        start_price = random.uniform(20, 500)

        prices = [start_price]
        for _ in range(days):
            trend = 0.3
            volatility = random.uniform(-2, 2.5)
            change = trend + volatility
            prices.append(prices[-1] * (1 + change / 100))

        base_volume = random.randint(5000000, 50000000)
        volumes = [int(base_volume * random.uniform(0.5, 2)) for _ in range(days)]

        data[symbol] = (prices, volumes)

    return data


# --- KULLANICI DURUMLARI ---
user_states: Dict[int, UserState] = {}

# --- OTOMATIK İZLEME ---
from stock_monitor import StockMonitor, AutoNotificationService

# Global monitor instance
monitor: Optional[StockMonitor] = None
notification_service: Optional[AutoNotificationService] = None


def init_monitor(bot_token: str, chat_id: str):
    """Monitor'ü başlatır"""
    global monitor, notification_service
    monitor = StockMonitor(bot_token, chat_id)
    notification_service = AutoNotificationService(monitor)
    return monitor, notification_service


# --- BOT ÇALIŞTIRMA ---
def run_bot(bot_token: str):
    """Bot'u çalıştırır"""
    # Monitor'ü başlat (varsayılan chat_id ile)
    init_monitor(bot_token, "0")  # Chat ID daha sonra güncellenecek

    application = Application.builder().token(bot_token).build()

    # Komut işleyicileri
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("yardim", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fiyat", price_command))
    application.add_handler(CommandHandler("analiz", analysis_command))
    application.add_handler(CommandHandler("yuklenenler", rising_stocks_command))
    application.add_handler(CommandHandler("uyari", alert_command))
    application.add_handler(CommandHandler("uyarilarim", my_alerts_command))
    application.add_handler(CommandHandler("gecmis", history_command))

    # YENİ: Otomatik izleme komutları
    application.add_handler(CommandHandler("izle", watch_command))
    application.add_handler(CommandHandler("izlemeyi_birak", unwatch_command))
    application.add_handler(CommandHandler("baslat_bildirim", start_alerts_command))
    application.add_handler(CommandHandler("izlemelerim", my_watches_command))

    # Bilinmeyen mesajlar
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    logger.info("🤖 Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# --- ANA PROGRAM ---
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN ayarlanmamış!")
        print("   .env dosyasına bot token'ınızı ekleyin.")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        exit(1)

    print("✅ Bot hazır! Ctrl+C ile durdurun.")
    run_bot(BOT_TOKEN)
