"""
Mevcut Hisse Alım Satım Uygulamanıza Entegrasyon Örneği
Bu dosyayı kendi projenize uyarlayarak kullanın.
"""

import time
import schedule
from telegram_notifier import TelegramNotifier, PriceAlertManager
from config import load_config


def integrate_with_your_trading_app():
    """
    Mevcut uygulamanıza entegre etmek için bu fonksiyonu kullanın.
    """

    # 1. Yapılandırmayı yükle
    telegram_config, alert_config, trading_config = load_config()

    # 2. Notifier oluştur
    notifier = TelegramNotifier(
        bot_token=telegram_config.bot_token,
        chat_id=telegram_config.chat_id
    )

    # 3. Uyarı yöneticisi oluştur
    alert_manager = PriceAlertManager(notifier)

    # 4. Uyarılar ekle
    alert_manager.add_alert("THYAO", target_price=190.00, alert_type="above")
    alert_manager.add_alert("THYAO", target_price=175.00, alert_type="below")
    alert_manager.add_alert("GARAN", target_price=50.00, alert_type="above")
    alert_manager.add_alert("EREGL", target_price=35.00, alert_type="below")

    return notifier, alert_manager


def example_price_check_function(symbol: str) -> float:
    """
    Örnek: Borsa API'sinden fiyat alma fonksiyonu
    Kendi API entegrasyonunuzu buraya ekleyin.
    """
    # TODO: Kendi fiyat veri kaynağınızı entegre edin
    # Örnek: return yfinance_api.get_price(symbol)
    return 0.0  # Şimdilik placeholder


def monitoring_loop(notifier: TelegramNotifier, alert_manager: PriceAlertManager):
    """
    Fiyat izleme döngüsü
    """
    while True:
        # İzlenecek hisseler
        symbols = ["THYAO", "GARAN", "EREGL", "ASELS", "KCHOL"]

        for symbol in symbols:
            try:
                # Fiyatı al (kendi API'nizi kullanın)
                current_price = example_price_check_function(symbol)

                if current_price > 0:
                    # Uyarıları kontrol et
                    alert_manager.check_alerts(symbol, current_price)

            except Exception as e:
                notifier.send_error_alert(
                    error_type="PriceCheck",
                    error_message=str(e),
                    details=f"Symbol: {symbol}"
                )

        # 60 saniye bekle
        time.sleep(60)


def example_trade_integration(notifier: TelegramNotifier):
    """
    İşlem gerçekleştiğinde bildirim gönderme örneği
    """
    # Alım işlemi
    notifier.send_trade_notification(
        symbol="THYAO",
        action="BUY",
        quantity=100,
        price=182.50,
        total_value=18250.00
    )

    # Satış işlemi
    notifier.send_trade_notification(
        symbol="GARAN",
        action="SELL",
        quantity=50,
        price=48.75,
        total_value=2437.50
    )


def example_portfolio_update(notifier: TelegramNotifier):
    """
    Portföy güncelleme örneği
    """
    notifier.send_portfolio_update(
        total_value=150000.00,
        daily_change=2500.00,
        daily_change_percent=1.69,
        top_gainers=[
            {"symbol": "THYAO", "change": 3.25},
            {"symbol": "ASELS", "change": 2.10},
        ],
        top_losers=[
            {"symbol": "EREGL", "change": -1.50},
        ]
    )


class TradingBot:
    """
    Telegram entegrasyonlu örnek trading bot sınıfı
    """

    def __init__(self, bot_token: str, chat_id: str):
        self.notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        self.alert_manager = PriceAlertManager(self.notifier)
        self.positions = {}  # Açık pozisyonlar

    def execute_buy(
        self,
        symbol: str,
        quantity: int,
        price: float
    ) -> dict:
        """Alım işlemi gerçekleştir ve bildirim gönder"""
        total = quantity * price

        # İşlemi kaydet
        self.positions[symbol] = {
            "quantity": quantity,
            "entry_price": price,
            "total": total
        }

        # Telegram bildirimi
        self.notifier.send_trade_notification(
            symbol=symbol,
            action="BUY",
            quantity=quantity,
            price=price,
            total_value=total
        )

        # Fiyat uyarısı ekle
        self.alert_manager.add_alert(
            symbol=symbol,
            target_price=price * 1.05,  # %5 kar hedefi
            alert_type="above"
        )
        self.alert_manager.add_alert(
            symbol=symbol,
            target_price=price * 0.95,  # %5 zarar kes
            alert_type="below"
        )

        return {"status": "success", "symbol": symbol, "quantity": quantity}

    def execute_sell(self, symbol: str, quantity: int, price: float) -> dict:
        """Satış işlemi gerçekleştir ve bildirim gönder"""
        total = quantity * price

        if symbol in self.positions:
            entry = self.positions[symbol]["entry_price"]
            pnl = (price - entry) * quantity
            pnl_percent = ((price - entry) / entry) * 100

            self.notifier.send_price_alert(
                symbol=symbol,
                current_price=price,
                previous_price=entry,
                alert_type="percent_change"
            )

            del self.positions[symbol]

        self.notifier.send_trade_notification(
            symbol=symbol,
            action="SELL",
            quantity=quantity,
            price=price,
            total_value=total
        )

        return {"status": "success", "symbol": symbol, "quantity": quantity}

    def check_prices(self, prices: dict):
        """Tüm fiyatları kontrol et"""
        for symbol, price in prices.items():
            self.alert_manager.check_alerts(symbol, price)


# Kullanım örneği
if __name__ == "__main__":
    # Yapılandırmayı yükle
    telegram_config, _, _ = load_config()

    # Bot oluştur
    bot = TradingBot(
        bot_token=telegram_config.bot_token,
        chat_id=telegram_config.chat_id
    )

    # Örnek alım
    bot.execute_buy("THYAO", 100, 180.00)

    # Fiyat kontrolü
    prices = {
        "THYAO": 185.00,
        "GARAN": 49.50,
        "EREGL": 34.00
    }
    bot.check_prices(prices)
