"""
Telegram Fiyat Uyarı Bildirim Modülü
Hisse alım satım uygulamaları için Telegram entegrasyonu

Kullanım:
    from telegram_notifier import TelegramNotifier

    notifier = TelegramNotifier(bot_token="YOUR_BOT_TOKEN", chat_id="YOUR_CHAT_ID")
    notifier.send_price_alert(symbol="THYAO", current_price=180.50, target_price=185.00, alert_type="above")
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
import json

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    raise ImportError("python-telegram-bot kütüphanesi kurulu değil. pip install python-telegram-bot komutunu çalıştırın.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Fiyat uyarı türleri"""
    ABOVE = "above"
    BELOW = "below"
    PERCENT_CHANGE = "percent_change"
    VOLUME_SPIKE = "volume_spike"


class TelegramNotifier:
    """
    Telegram botu üzerinden fiyat uyarıları gönderir.

    Args:
        bot_token: Telegram Bot API token (BotFather'dan alınır)
        chat_id: Mesajların gönderileceği sohbet ID'si
        parse_mode: Mesaj formatlama modu ('HTML', 'Markdown', None)
    """

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        parse_mode: Optional[str] = "HTML"
    ):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.parse_mode = parse_mode
        self.bot = Bot(token=bot_token)
        self._alert_history: list = []

    async def _send_message(self, text: str) -> bool:
        """Asenkron mesaj gönderme"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=self.parse_mode
            )
            logger.info(f"Mesaj gönderildi: {text[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Telegram hatası: {e}")
            return False

    def send_message_sync(self, text: str) -> bool:
        """Senkron mesaj gönderme (bloklayıcı)"""
        try:
            asyncio.run(self._send_message(text))
            return True
        except Exception as e:
            logger.error(f"Gönderim hatası: {e}")
            return False

    def send_price_alert(
        self,
        symbol: str,
        current_price: float,
        target_price: Optional[float] = None,
        previous_price: Optional[float] = None,
        alert_type: str = "above",
        exchange: str = "BIST"
    ) -> bool:
        """
        Fiyat uyarısı gönderir.

        Args:
            symbol: Hisse senedi sembolü (örn: 'THYAO', 'GARAN')
            current_price: Güncel fiyat
            target_price: Hedef fiyat (alert_type 'above' veya 'below' için)
            previous_price: Önceki fiyat (yüzde değişim hesaplaması için)
            alert_type: Uyarı türü ('above', 'below', 'percent_change', 'volume_spike')
            exchange: Borsa/Exchange adı

        Returns:
            bool: Mesaj başarıyla gönderildi mi
        """
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        # Emoji seçimi
        emojis = {
            "above": "🔴",
            "below": "🟢",
            "percent_change": "📊",
            "volume_spike": "📈"
        }
        emoji = emojis.get(alert_type, "🔔")

        # Mesaj oluşturma
        if alert_type == "above":
            message = (
                f"{emoji} <b>FİYAT UYARISI</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Sembol: <code>{exchange}:{symbol}</code>\n"
                f"💰 Güncel Fiyat: <b>{current_price:,.2f} TL</b>\n"
                f"🎯 Hedef Fiyat: {target_price:,.2f} TL\n"
                f"📈 Durum: Hedef fiyat aşıldı!\n"
                f"⏰ Zaman: {timestamp}"
            )
        elif alert_type == "below":
            message = (
                f"{emoji} <b>FİYAT UYARISI</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Sembol: <code>{exchange}:{symbol}</code>\n"
                f"💰 Güncel Fiyat: <b>{current_price:,.2f} TL</b>\n"
                f"🎯 Hedef Fiyat: {target_price:,.2f} TL\n"
                f"📉 Durum: Alt sınır aşıldı!\n"
                f"⏰ Zaman: {timestamp}"
            )
        elif alert_type == "percent_change" and previous_price:
            change = ((current_price - previous_price) / previous_price) * 100
            direction = "📈 Yukarı" if change > 0 else "📉 Aşağı"
            message = (
                f"{emoji} <b>FİYAT DEĞİŞİMİ</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Sembol: <code>{exchange}:{symbol}</code>\n"
                f"💵 Önceki: {previous_price:,.2f} TL\n"
                f"💰 Güncel: <b>{current_price:,.2f} TL</b>\n"
                f"{direction}: <b>{change:+.2f}%</b>\n"
                f"⏰ Zaman: {timestamp}"
            )
        else:
            message = (
                f"{emoji} <b>GENEL FİYAT BİLGİSİ</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Sembol: <code>{exchange}:{symbol}</code>\n"
                f"💰 Fiyat: <b>{current_price:,.2f} TL</b>\n"
                f"⏰ Zaman: {timestamp}"
            )

        # Geçmişe kaydet
        self._alert_history.append({
            "symbol": symbol,
            "price": current_price,
            "type": alert_type,
            "timestamp": timestamp
        })

        return self.send_message_sync(message)

    def send_trade_notification(
        self,
        symbol: str,
        action: str,  # "BUY" veya "SELL"
        quantity: int,
        price: float,
        total_value: float,
        exchange: str = "BIST"
    ) -> bool:
        """
        İşlem (alım/satım) bildirimi gönderir.

        Args:
            symbol: Hisse senedi sembolü
            action: İşlem tipi ('BUY' veya 'SELL')
            quantity: Adet
            price: İşlem fiyatı
            total_value: Toplam işlem değeri
            exchange: Borsa adı
        """
        emoji = "🟢" if action.upper() == "BUY" else "🔴"
        action_tr = "ALIM" if action.upper() == "BUY" else "SATIM"

        message = (
            f"{emoji} <b>İŞLEM GERÇEKLEŞTİ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Sembol: <code>{exchange}:{symbol}</code>\n"
            f"📋 İşlem: <b>{action_tr}</b>\n"
            f"🔢 Adet: {quantity:,} lot\n"
            f"💵 Fiyat: {price:,.2f} TL\n"
            f"💰 Toplam: <b>{total_value:,.2f} TL</b>\n"
            f"⏰ Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

        return self.send_message_sync(message)

    def send_portfolio_update(
        self,
        total_value: float,
        daily_change: float,
        daily_change_percent: float,
        top_gainers: list = None,
        top_losers: list = None
    ) -> bool:
        """
        Portföy özeti gönderir.
        """
        emoji = "🟢" if daily_change >= 0 else "🔴"
        sign = "+" if daily_change >= 0 else ""

        top_stocks = ""
        if top_gainers:
            top_stocks += "\n🏆 <b>En Çok Kazananlar:</b>\n"
            for stock in top_gainers[:3]:
                top_stocks += f"  • {stock['symbol']}: {stock['change']:+.2f}%\n"
        if top_losers:
            top_stocks += "\n📉 <b>En Çok Kaybedenler:</b>\n"
            for stock in top_losers[:3]:
                top_stocks += f"  • {stock['symbol']}: {stock['change']:+.2f}%\n"

        message = (
            f"📊 <b>GÜNLÜK PORTFÖY ÖZETİ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💼 Toplam Değer: <b>{total_value:,.2f} TL</b>\n"
            f"{emoji} Günlük Değişim: <b>{sign}{daily_change:,.2f} TL ({sign}{daily_change_percent:.2f}%)</b>\n"
            f"{top_stocks}"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        return self.send_message_sync(message)

    def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        details: Optional[str] = None
    ) -> bool:
        """Sistem hata bildirimi gönderir."""
        message = (
            f"⚠️ <b>SİSTEM HATASI</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ Tür: {error_type}\n"
            f"📝 Mesaj: {error_message}\n"
        )
        if details:
            message += f"🔍 Detay: {details}\n"
        message += f"⏰ Zaman: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"

        return self.send_message_sync(message)

    def get_alert_history(self) -> list:
        """Gönderilen uyarı geçmişini döndürür."""
        return self._alert_history.copy()

    def save_alert_history(self, filepath: str = "alert_history.json") -> None:
        """Uyarı geçmişini JSON dosyasına kaydeder."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._alert_history, f, ensure_ascii=False, indent=2)


class PriceAlertManager:
    """
    Fiyat uyarılarını yönetir ve izler.

    Args:
        notifier: TelegramNotifier örneği
    """

    def __init__(self, notifier: TelegramNotifier):
        self.notifier = notifier
        self.alerts: dict = {}

    def add_alert(
        self,
        symbol: str,
        target_price: float,
        alert_type: str = "above",
        exchange: str = "BIST"
    ) -> str:
        """
        Yeni bir fiyat uyarısı ekler.

        Returns:
            str: Uyarı ID'si
        """
        alert_id = f"{symbol}_{target_price}_{datetime.now().timestamp()}"
        self.alerts[alert_id] = {
            "symbol": symbol,
            "target_price": target_price,
            "alert_type": alert_type,
            "exchange": exchange,
            "created_at": datetime.now().isoformat(),
            "triggered": False
        }
        logger.info(f"Uyarı eklendi: {alert_id}")
        return alert_id

    def check_alerts(self, symbol: str, current_price: float) -> list:
        """
        Fiyatı kontrol eder ve tetiklenen uyarıları döndürür.

        Args:
            symbol: Hisse senedi sembolü
            current_price: Güncel fiyat

        Returns:
            list: Tetiklenen uyarı listesi
        """
        triggered = []

        for alert_id, alert in self.alerts.items():
            if alert["symbol"] != symbol or alert["triggered"]:
                continue

            target = alert["target_price"]

            if alert["alert_type"] == "above" and current_price >= target:
                self.notifier.send_price_alert(
                    symbol=symbol,
                    current_price=current_price,
                    target_price=target,
                    alert_type="above",
                    exchange=alert["exchange"]
                )
                alert["triggered"] = True
                triggered.append(alert_id)

            elif alert["alert_type"] == "below" and current_price <= target:
                self.notifier.send_price_alert(
                    symbol=symbol,
                    current_price=current_price,
                    target_price=target,
                    alert_type="below",
                    exchange=alert["exchange"]
                )
                alert["triggered"] = True
                triggered.append(alert_id)

        return triggered

    def remove_alert(self, alert_id: str) -> bool:
        """Uyarıyı kaldırır."""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return True
        return False

    def get_active_alerts(self, symbol: Optional[str] = None) -> dict:
        """Aktif uyarıları döndürür."""
        if symbol:
            return {
                k: v for k, v in self.alerts.items()
                if v["symbol"] == symbol and not v["triggered"]
            }
        return {k: v for k, v in self.alerts.items() if not v["triggered"]}


# Örnek kullanım
if __name__ == "__main__":
    # !!! Gerçek token ve chat ID'nizi girin !!!
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    CHAT_ID = "YOUR_CHAT_ID_HERE"

    # Notifier oluşturma
    notifier = TelegramNotifier(bot_token=BOT_TOKEN, chat_id=CHAT_ID)

    # Test mesajı
    notifier.send_price_alert(
        symbol="THYAO",
        current_price=185.50,
        target_price=185.00,
        alert_type="above"
    )
