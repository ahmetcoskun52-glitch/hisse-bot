"""
Telegram Bildirim Yapılandırması
Ortam değişkenlerinden veya .env dosyasından ayarları yükler.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelegramConfig:
    """Telegram yapılandırma ayarları"""
    bot_token: str
    chat_id: str
    parse_mode: str = "HTML"
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        """Ortam değişkenlerinden yapılandırma oluşturur"""
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            parse_mode=os.getenv("TELEGRAM_PARSE_MODE", "HTML"),
            enabled=os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Yapılandırmanın geçerli olup olmadığını kontrol eder"""
        if not self.enabled:
            return True, None
        if not self.bot_token:
            return False, "TELEGRAM_BOT_TOKEN ayarlanmamış"
        if not self.chat_id:
            return False, "TELEGRAM_CHAT_ID ayarlanmamış"
        return True, None


@dataclass
class PriceAlertConfig:
    """Fiyat uyarısı yapılandırması"""
    check_interval: int = 60  # Saniye
    min_change_percent: float = 0.5  # Minimum değişim yüzdesi
    max_alerts_per_hour: int = 10  # Saat başına max uyarı

    @classmethod
    def from_env(cls) -> "PriceAlertConfig":
        return cls(
            check_interval=int(os.getenv("ALERT_CHECK_INTERVAL", "60")),
            min_change_percent=float(os.getenv("MIN_CHANGE_PERCENT", "0.5")),
            max_alerts_per_hour=int(os.getenv("MAX_ALERTS_PER_HOUR", "10"))
        )


@dataclass
class TradingConfig:
    """Ticaret yapılandırması"""
    default_exchange: str = "BIST"
    notification_on_trade: bool = True
    notification_on_portfolio_update: bool = True
    portfolio_update_interval: int = 300  # 5 dakika

    @classmethod
    def from_env(cls) -> "TradingConfig":
        return cls(
            default_exchange=os.getenv("DEFAULT_EXCHANGE", "BIST"),
            notification_on_trade=os.getenv("NOTIFY_TRADES", "true").lower() == "true",
            notification_on_portfolio_update=os.getenv("NOTIFY_PORTFOLIO", "true").lower() == "true",
            portfolio_update_interval=int(os.getenv("PORTFOLIO_INTERVAL", "300"))
        )


def load_config() -> tuple[TelegramConfig, PriceAlertConfig, TradingConfig]:
    """Tüm yapılandırmaları yükler"""
    telegram = TelegramConfig.from_env()
    alerts = PriceAlertConfig.from_env()
    trading = TradingConfig.from_env()

    return telegram, alerts, trading
