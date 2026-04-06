"""
Hisse İzleme ve Otomatik Bildirim Modülü - Final Versiyon
Gelişmiş Yükseliş Tespiti + Ayarlanabilir Bildirim Sıklığı
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StockSignal:
    """Hisse sinyali"""
    symbol: str
    signal_type: str  # "trend_reversal", "rising_start", "sudden_rally", "breakout"
    price: float
    previous_price: float
    change_percent: float
    score: float
    target_price: float
    trend: str
    rsi: float
    timestamp: datetime
    message: str
    priority: str  # "high", "medium", "low"


@dataclass
class SignalHistory:
    """Sinyal geçmişi"""
    signal: StockSignal
    notified: bool = False
    notified_at: Optional[datetime] = None


@dataclass
class NotificationConfig:
    """Bildirim ayarları"""
    # Yükseliş tespit ayarları
    min_price_change: float = 2.0  # Minimum fiyat değişimi (%)
    min_volume_ratio: float = 1.5  # Minimum hacim artışı
    rsi_oversold_threshold: float = 40.0  # Aşırı satım RSI eşiği

    # Bildirim sıklığı
    cooldown_seconds: int = 600  # Aynı hisse için bekleme süresi (10 dk)
    scan_interval: int = 30  # Tarama aralığı (saniye) - daha sık!

    # Piyasa geneli
    market_wide_enabled: bool = True
    min_rally_percent: float = 2.5  # Ani yükseliş eşiği


class StockMonitor:
    """
    Gelişmiş hisse izleme servisi

    Yükselişe Geçiş Tespitleri:
    - Trend reversal (düşüş → yükseliş)
    - RSI crossover (30-40 → 50+)
    - Volume spike + price up
    - Breakout from consolidation
    """

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.screener = None
        self.analyzer = None

        # İzlenen hisseler
        self.watched_stocks: Set[str] = set()

        # Sinyal geçmişi
        self.signal_history: Dict[str, List[SignalHistory]] = defaultdict(list)

        # Bildirim ayarları
        self.config = NotificationConfig()

        # Son durumlar (geçiş tespiti için)
        self.last_rsi: Dict[str, float] = {}
        self.last_trend: Dict[str, str] = {}
        self.last_prices: Dict[str, float] = {}
        self.last_scores: Dict[str, float] = {}
        self.notification_count = 0

    def add_stock(self, symbol: str):
        """Hisseyi izleme listesine ekler"""
        self.watched_stocks.add(symbol.upper())
        logger.info(f"İzleme eklendi: {symbol}")

    def remove_stock(self, symbol: str):
        """Hisseyi izleme listesinden çıkarır"""
        self.watched_stocks.discard(symbol.upper())
        logger.info(f"İzleme kaldırıldı: {symbol}")

    def set_notification_frequency(self, seconds: int):
        """Bildirim/tarama sıklığını ayarlar"""
        self.config.scan_interval = max(15, seconds)  # Minimum 15 saniye
        logger.info(f"Tarama aralığı: {self.config.scan_interval}s")

    def set_cooldown(self, seconds: int):
        """Bildirim cooldown süresini ayarlar"""
        self.config.cooldown_seconds = max(60, seconds)  # Minimum 1 dakika
        logger.info(f"Cooldown: {self.config.cooldown_seconds}s")

    def should_notify(self, symbol: str, signal_type: str) -> bool:
        """Bildirim gönderilmeli mi kontrol eder"""
        now = datetime.now()

        if symbol in self.signal_history:
            for history in reversed(self.signal_history[symbol][-3:]):
                if history.signal.signal_type == signal_type:
                    time_diff = (now - history.signal.timestamp).total_seconds()
                    if time_diff < self.config.cooldown_seconds:
                        return False

        return True

    def detect_rising_start(
        self,
        symbol: str,
        current_price: float,
        prices: List[float],
        volumes: List[int],
        recommendation
    ) -> Optional[StockSignal]:
        """
        Yükselişe başlama anını tespit eder!

        Tespit Edilen Durumlar:
        1. Trend Reversal: Düşüş/Nötr → Yükseliş
        2. RSI Crossover: 30-40 bölgesinden 50+ geçişi
        3. Volume + Price Surge: Hacim + Fiyat artışı
        4. Breakout: Konsolidasyondan çıkış
        """
        if not recommendation:
            return None

        current_rsi = recommendation.rsi
        current_trend = recommendation.trend

        # Önceki değerler
        last_rsi = self.last_rsi.get(symbol, 50)
        last_trend = self.last_trend.get(symbol, "neutral")
        last_price = self.last_prices.get(symbol, current_price)

        # Fiyat değişimi
        price_change = ((current_price - last_price) / last_price) * 100 if last_price else 0

        # Hacim kontrolü
        avg_volume = np.mean(volumes[-10:]) if len(volumes) >= 10 else volumes[-1]
        current_volume = volumes[-1] if volumes else 0
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        signal = None
        signal_type = None
        priority = "medium"

        # 1️⃣ TREND REVERSAL (Düşüş → Yükseliş)
        if (last_trend in ["bearish", "neutral"] and
            current_trend in ["bullish", "strong_bullish"]):
            signal_type = "trend_reversal"
            priority = "high"

            if current_trend == "strong_bullish":
                priority = "high"

            signal = self._create_trend_reversal_message(
                symbol, current_price, price_change, current_trend,
                current_rsi, recommendation, last_trend
            )

        # 2️⃣ RSI CROSSOVER (Aşırı satımdan çıkış)
        elif (last_rsi < self.config.rsi_oversold_threshold and
              current_rsi >= 50 and
              current_rsi > last_rsi):
            signal_type = "rsi_crossover"
            priority = "high"

            signal = self._create_rsi_crossover_message(
                symbol, current_price, price_change, current_rsi,
                last_rsi, recommendation
            )

        # 3️⃣ VOLUME + PRICE SURGE (Güçlü alım)
        elif (price_change >= self.config.min_price_change and
              volume_ratio >= self.config.min_volume_ratio):
            signal_type = "volume_surge"
            priority = "high"

            signal = self._create_volume_surge_message(
                symbol, current_price, price_change, volume_ratio,
                current_rsi, recommendation
            )

        # 4️⃣ BREAKOUT (Konsolidasyondan çıkış)
        elif (current_trend in ["bullish", "strong_bullish"] and
              last_trend == "neutral" and
              price_change >= 1.5):
            signal_type = "breakout"
            priority = "medium"

            signal = self._create_breakout_message(
                symbol, current_price, price_change, recommendation
            )

        # Durumları güncelle
        self.last_rsi[symbol] = current_rsi
        self.last_trend[symbol] = current_trend
        self.last_prices[symbol] = current_price
        self.last_scores[symbol] = recommendation.score

        if signal:
            signal.priority = priority
            return signal

        return None

    def _create_trend_reversal_message(self, symbol, price, change, trend, rsi, rec, old_trend) -> StockSignal:
        """Trend reversal mesajı"""
        trend_emoji = "🟢🟢" if trend == "strong_bullish" else "🟢"

        return StockSignal(
            symbol=symbol,
            signal_type="trend_reversal",
            price=price,
            previous_price=price * 0.97,
            change_percent=change,
            score=rec.score,
            target_price=rec.targets[0].target_price if rec.targets else price * 1.05,
            trend=trend,
            rsi=rsi,
            timestamp=datetime.now(),
            message=(
                f"{trend_emoji} <b>YÜKSELİŞ BAŞLADI!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{symbol}</b>\n"
                f"⚡ <b>Trend reversal tespit!</b>\n"
                f"   {old_trend.title()} → {trend.replace('_', ' ').title()}\n\n"
                f"💰 Fiyat: <b>{price:,.2f} TL</b>\n"
                f"📈 Değişim: <b>{change:+.2f}%</b>\n"
                f"📊 RSI: {rsi:.1f}\n"
                f"🎯 Hedef: {rec.targets[0].target_price if rec.targets else price*1.05:,.2f} TL\n"
                f"🛡️ Zarar Kes: {rec.stop_loss:,.2f} TL\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 <i>Yükseliş trendine geçti! Giriş sinyali!</i>\n"
                f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            priority="high"
        )

    def _create_rsi_crossover_message(self, symbol, price, change, rsi, old_rsi, rec) -> StockSignal:
        """RSI crossover mesajı"""
        return StockSignal(
            symbol=symbol,
            signal_type="rsi_crossover",
            price=price,
            previous_price=price * 0.98,
            change_percent=change,
            score=rec.score,
            target_price=rec.targets[0].target_price if rec.targets else price * 1.05,
            trend=rec.trend,
            rsi=rsi,
            timestamp=datetime.now(),
            message=(
                f"🟢 <b>RSİ CROSSOVER!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{symbol}</b>\n"
                f"⚡ <b>RSI {old_rsi:.0f} → {rsi:.0f}</b>\n"
                f"   Aşırı satımdan çıkış!\n\n"
                f"💰 Fiyat: <b>{price:,.2f} TL</b>\n"
                f"📊 RSI: {rsi:.1f} (Güçlü momentum)\n"
                f"📈 Değişim: {change:+.2f}%\n"
                f"🎯 Hedef: {rec.targets[0].target_price if rec.targets else price*1.05:,.2f} TL\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 <i>Alım gücü artıyor! Momentum güçleniyor!</i>\n"
                f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            priority="high"
        )

    def _create_volume_surge_message(self, symbol, price, change, vol_ratio, rsi, rec) -> StockSignal:
        """Volume surge mesajı"""
        return StockSignal(
            symbol=symbol,
            signal_type="volume_surge",
            price=price,
            previous_price=price * 0.98,
            change_percent=change,
            score=rec.score,
            target_price=rec.targets[0].target_price if rec.targets else price * 1.05,
            trend=rec.trend,
            rsi=rsi,
            timestamp=datetime.now(),
            message=(
                f"🚀 <b>HACİM PATLAMASI!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{symbol}</b>\n"
                f"⚡ <b>Yüksek işlem hacmi!</b>\n"
                f"   Güçlü alım baskını var!\n\n"
                f"💰 Fiyat: <b>{price:,.2f} TL</b>\n"
                f"📈 Değişim: <b>{change:+.2f}%</b>\n"
                f"📊 Hacim: <b>{vol_ratio:.1f}x</b> normal\n"
                f"📊 RSI: {rsi:.1f}\n"
                f"🎯 Hedef: {rec.targets[0].target_price if rec.targets else price*1.05:,.2f} TL\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 <i>Dikkat çeken bir hisse! Yükseliş sinyali!</i>\n"
                f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            priority="high"
        )

    def _create_breakout_message(self, symbol, price, change, rec) -> StockSignal:
        """Breakout mesajı"""
        return StockSignal(
            symbol=symbol,
            signal_type="breakout",
            price=price,
            previous_price=price * 0.99,
            change_percent=change,
            score=rec.score,
            target_price=rec.targets[0].target_price if rec.targets else price * 1.03,
            trend=rec.trend,
            rsi=rec.rsi,
            timestamp=datetime.now(),
            message=(
                f"📈 <b>BREAKOUT!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{symbol}</b>\n"
                f"⚡ Konsolidasyondan çıkış!\n\n"
                f"💰 Fiyat: <b>{price:,.2f} TL</b>\n"
                f"📈 Değişim: <b>{change:+.2f}%</b>\n"
                f"🎯 Hedef: {rec.targets[0].target_price if rec.targets else price*1.03:,.2f} TL\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            priority="medium"
        )

    def detect_sudden_rally(self, symbol: str, current_price: float, previous_price: float,
                           current_volume: int, avg_volume: float, trend: str, score: float) -> Optional[StockSignal]:
        """Ani yükseliş tespit eder (izleme listesinde olmayan hisseler dahil)"""
        price_change_pct = ((current_price - previous_price) / previous_price) * 100
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        is_rally = (
            price_change_pct >= self.config.min_rally_percent and
            volume_ratio >= 1.5 and
            "bullish" in trend
        )

        if is_rally:
            message = (
                f"🚀 <b>ANİ YÜKSELİŞ!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>{symbol}</b>\n"
                f"⚡ İzleme listenizde YOK!\n"
                f"💰 Fiyat: <b>{current_price:,.2f} TL</b>\n"
                f"📈 Değişim: <b>{price_change_pct:+.2f}%</b>\n"
                f"📊 Hacim: {volume_ratio:.1f}x normal\n"
                f"📊 Skor: {score:.0f}/100\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 İzleme listesine eklemek ister misiniz?\n"
                f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )

            return StockSignal(
                symbol=symbol,
                signal_type="sudden_rally",
                price=current_price,
                previous_price=previous_price,
                change_percent=price_change_pct,
                score=score,
                target_price=current_price * 1.05,
                trend=trend,
                rsi=50,
                timestamp=datetime.now(),
                message=message,
                priority="medium"
            )

        return None

    def check_and_notify(self, symbol: str, current_price: float,
                        prices: List[float], volumes: List[int]) -> Optional[StockSignal]:
        """Hisse için detaylı sinyal kontrolü"""
        try:
            from stock_screener import StockScreener
        except ImportError:
            return None

        if not self.screener:
            self.screener = StockScreener()

        recommendation = self.screener.analyze_stock(symbol, prices, volumes)
        if not recommendation:
            return None

        # Yükselişe başlama tespiti (ANA ÖZELLIK!)
        rising_signal = self.detect_rising_start(
            symbol, current_price, prices, volumes, recommendation
        )

        if rising_signal and self.should_notify(symbol, rising_signal.signal_type):
            return rising_signal

        return None

    def get_watched_stocks(self) -> List[str]:
        """İzlenen hisseleri döndürür"""
        return sorted(list(self.watched_stocks))

    def get_status(self) -> str:
        """Sistem durumunu döndürür"""
        return (
            f"📊 <b>Sistem Durumu</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👁️ İzlenen: {len(self.watched_stocks)} hisse\n"
            f"⏱️ Tarama: {self.config.scan_interval}s\n"
            f"🕐 Cooldown: {self.config.cooldown_seconds}s\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )


class AutoNotificationService:
    """Otomatik bildirim servisi"""

    def __init__(self, monitor: StockMonitor):
        self.monitor = monitor
        self.running = False

    async def send_telegram_message(self, message: str) -> bool:
        """Telegram'a mesaj gönderir"""
        try:
            from telegram import Bot
            bot = Bot(token=self.monitor.bot_token)
            await bot.send_message(
                chat_id=self.monitor.chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Telegram mesaj hatası: {e}")
            return False

    async def scan_and_notify(self, stock_data: Dict[str, Tuple[List[float], List[int]]]) -> int:
        """Hisseleri tarar ve bildirim gönderir"""
        signals_sent = 0

        for symbol, (prices, volumes) in stock_data.items():
            if len(prices) < 20 or len(volumes) < 20:
                continue

            current_price = prices[-1]
            previous_price = prices[-3] if len(prices) >= 3 else prices[0]
            current_volume = volumes[-1] if volumes else 0
            avg_volume = np.mean(volumes[-10:]) if len(volumes) >= 10 else 1

            # İzlenen hisseler için yükseliş tespiti
            if symbol in self.monitor.watched_stocks:
                signal = self.monitor.check_and_notify(symbol, current_price, prices, volumes)

                if signal and self.monitor.should_notify(symbol, signal.signal_type):
                    success = await self.send_telegram_message(signal.message)
                    if success:
                        signals_sent += 1
                        self.monitor.notification_count += 1
                        self.monitor.signal_history[symbol].append(
                            SignalHistory(signal=signal, notified=True, notified_at=datetime.now())
                        )

            # Piyasa geneli ani yükseliş taraması
            elif self.monitor.config.market_wide_enabled:
                from stock_screener import StockScreener
                screener = StockScreener()
                recommendation = screener.analyze_stock(symbol, prices, volumes)

                if recommendation:
                    rally = self.monitor.detect_sudden_rally(
                        symbol, current_price, previous_price,
                        current_volume, avg_volume,
                        recommendation.trend, recommendation.score
                    )

                    if rally and self.monitor.should_notify(symbol, "sudden_rally"):
                        success = await self.send_telegram_message(rally.message)
                        if success:
                            signals_sent += 1
                            self.monitor.notification_count += 1

        return signals_sent

    async def run_periodic_scan(self, stock_data_func, scan_interval: int = 30):
        """Periyodik tarama başlatır"""
        import asyncio

        self.running = True
        logger.info(f"Periyodik tarama başladı (aralık: {scan_interval}s)")

        while self.running:
            try:
                stock_data = stock_data_func()
                signals = await self.scan_and_notify(stock_data)

                if signals > 0:
                    logger.info(f"Tarama: {signals} bildirim gönderildi")

            except Exception as e:
                logger.error(f"Tarama hatası: {e}")

            await asyncio.sleep(scan_interval)

    def stop(self):
        """Taramayı durdurur"""
        self.running = False
