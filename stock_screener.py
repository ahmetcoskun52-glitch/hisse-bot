"""
Hisse Senedi Tarama Modülü - Gelişmiş Versiyon
Yükseliş potansiyeli olan hisseleri analiz eder ve hedef fiyatlar hesaplar
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class PriceTarget:
    """Fiyat hedefi"""
    period: str  # "1H", "1G", "1A"
    target_price: float
    change_percent: float
    confidence: float  # Güven skoru (0-100)


@dataclass
class StockRecommendation:
    """Hisse önerisi"""
    symbol: str
    name: str
    current_price: float
    entry_price: float  # Giriş noktası
    stop_loss: float  # Zarar kes
    targets: List[PriceTarget]  # Hedefler
    trend: str  # "strong_bullish", "bullish", "neutral"
    score: float
    rsi: float
    volume_signal: str
    analysis: str  # Kısa analiz


@dataclass
class ScanResult:
    """Tarama sonucu"""
    stocks: List[StockRecommendation]
    scan_time: datetime
    timeframe: str


class StockScreener:
    """
    Gelişmiş hisse tarama sınıfı
    Kısa vadeli hedef fiyatlar ve detaylı analiz sunar
    """

    def __init__(self):
        self.min_volume = 1000000
        self.min_score = 55

    def analyze_stock(
        self,
        symbol: str,
        prices: List[float],
        volumes: List[int]
    ) -> Optional[StockRecommendation]:
        """
        Hisse için detaylı analiz yapar.

        Args:
            symbol: Hisse sembolü
            prices: Fiyat listesi
            volumes: Hacim listesi

        Returns:
            StockRecommendation nesnesi veya None
        """
        if len(prices) < 20 or len(volumes) < 20:
            return None

        current_price = prices[-1]

        # Teknik göstergeleri hesapla
        rsi = self._calculate_rsi(prices)
        macd = self._calculate_macd(prices)
        support, resistance = self._find_support_resistance(prices)
        trend = self._determine_trend(prices)

        # Hacim analizi
        avg_volume = np.mean(volumes[-10:])
        current_vol = volumes[-1]
        volume_ratio = current_vol / avg_volume if avg_volume > 0 else 1

        if volume_ratio > 1.5:
            volume_signal = "📈 Yüksek Hacim"
        elif volume_ratio > 1.2:
            volume_signal = "📊 Normal Üstü"
        else:
            volume_signal = "📉 Düşük Hacim"

        # Fiyat hedeflerini hesapla
        targets = self._calculate_targets(current_price, resistance, trend, rsi)

        # Skor hesapla
        score = self._calculate_score(prices, volumes, rsi, trend, volume_ratio)

        # Stop loss hesapla
        stop_loss = self._calculate_stop_loss(current_price, support, trend)

        # Analiz metni oluştur
        analysis = self._generate_analysis(trend, rsi, macd, volume_ratio)

        return StockRecommendation(
            symbol=symbol,
            name=self._get_stock_name(symbol),
            current_price=current_price,
            entry_price=current_price,  # Anlık giriş önerisi
            stop_loss=stop_loss,
            targets=targets,
            trend=trend,
            score=score,
            rsi=rsi,
            volume_signal=volume_signal,
            analysis=analysis
        )

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hesaplar"""
        if len(prices) < period + 1:
            return 50

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float]:
        """MACD hesaplar (signal, histogram)"""
        if len(prices) < 26:
            return 0, 0

        ema12 = self._ema(prices, 12)
        ema26 = self._ema(prices, 26)

        macd_line = ema12 - ema26
        signal_line = self._ema([macd_line] * len(prices[-9:]) if macd_line else [0], 9)

        return macd_line, macd_line - signal_line if signal_line else 0

    def _ema(self, prices: List[float], period: int) -> float:
        """Üssel hareketli ortalama"""
        if len(prices) < period:
            return prices[-1] if prices else 0

        prices_array = np.array(prices[-period:])
        multiplier = 2 / (period + 1)
        ema = prices_array[0]

        for price in prices_array[1:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _find_support_resistance(self, prices: List[float]) -> Tuple[float, float]:
        """Destek ve direnç seviyelerini bulur"""
        if len(prices) < 20:
            return min(prices), max(prices)

        # Son 20 günlük min/max
        recent = prices[-20:]
        support = min(recent) * 0.995  # %0.5 alt
        resistance = max(recent) * 1.005  # %0.5 üst

        return support, resistance

    def _determine_trend(self, prices: List[float]) -> str:
        """Trend belirler"""
        if len(prices) < 20:
            return "neutral"

        ma10 = np.mean(prices[-10:])
        ma20 = np.mean(prices[-20:])

        if prices[-1] > ma10 > ma20:
            return "strong_bullish"
        elif prices[-1] > ma10:
            return "bullish"
        elif prices[-1] < ma10 < ma20:
            return "strong_bearish"
        elif prices[-1] < ma10:
            return "bearish"
        return "neutral"

    def _calculate_targets(
        self,
        current_price: float,
        resistance: float,
        trend: str,
        rsi: float
    ) -> List[PriceTarget]:
        """Fiyat hedeflerini hesaplar"""

        # Trend'e göre hedefler belirle
        if trend in ["strong_bullish", "bullish"]:
            # Yükseliş trendinde hedefler
            short_target = current_price * 1.03  # +3% (1 gün)
            medium_target = current_price * 1.07  # +7% (1 hafta)
            long_target = current_price * 1.15   # +15% (1 ay)
        elif trend == "neutral":
            # Nötr trend
            short_target = current_price * 1.02
            medium_target = current_price * 1.05
            long_target = current_price * 1.10
        else:
            # Düşüş trendinde sınırlı hedef
            short_target = current_price * 1.01
            medium_target = current_price * 1.03
            long_target = current_price * 1.05

        # RSI'ya göre güven skoru
        if 40 <= rsi <= 60:
            confidence = 80
        elif 30 <= rsi <= 70:
            confidence = 65
        else:
            confidence = 50

        return [
            PriceTarget("1G", short_target, ((short_target - current_price) / current_price) * 100, confidence),
            PriceTarget("1H", medium_target, ((medium_target - current_price) / current_price) * 100, confidence - 10),
            PriceTarget("1A", long_target, ((long_target - current_price) / current_price) * 100, confidence - 20),
        ]

    def _calculate_stop_loss(
        self,
        current_price: float,
        support: float,
        trend: str
    ) -> float:
        """Stop loss hesaplar"""
        if trend in ["strong_bullish", "bullish"]:
            # Yükselişte sıkı stop loss
            return current_price * 0.97  # -3%
        elif trend == "neutral":
            return current_price * 0.95  # -5%
        else:
            return current_price * 0.92  # -8%

    def _calculate_score(
        self,
        prices: List[float],
        volumes: List[int],
        rsi: float,
        trend: str,
        volume_ratio: float
    ) -> float:
        """Genel yükseliş skoru hesaplar (0-100)"""
        score = 50

        # Trend katkısı (max +30)
        trend_scores = {
            "strong_bullish": 30,
            "bullish": 20,
            "neutral": 0,
            "bearish": -15,
            "strong_bearish": -30
        }
        score += trend_scores.get(trend, 0)

        # RSI katkısı (max +15, min -15)
        if 40 <= rsi <= 60:
            score += 15  # İdeal bölge
        elif 30 <= rsi <= 70:
            score += 5
        else:
            score -= 15

        # Hacim katkısı (max +10)
        if volume_ratio > 2:
            score += 10
        elif volume_ratio > 1.5:
            score += 7
        elif volume_ratio > 1.2:
            score += 4

        # Son 5 günlük performans (max +15)
        if len(prices) >= 5:
            recent_change = ((prices[-1] - prices[-5]) / prices[-5]) * 100
            score += min(max(recent_change, -10), 15)

        return max(0, min(100, score))

    def _generate_analysis(
        self,
        trend: str,
        rsi: float,
        macd: float,
        volume_ratio: float
    ) -> str:
        """Kısa analiz metni oluşturur"""
        analyses = []

        # Trend yorumu
        trend_texts = {
            "strong_bullish": "Güçlü yükseliş trendinde",
            "bullish": "Yükseliş trendinde",
            "neutral": "Yatay seyirde",
            "bearish": "Düşüş trendinde",
            "strong_bearish": "Güçlü düşüş trendinde"
        }
        analyses.append(trend_texts.get(trend, ""))

        # RSI yorumu
        if rsi > 70:
            analyses.append("Aşırı alım bölgesinde")
        elif rsi < 30:
            analyses.append("Aşırı satım bölgesinde")
        elif 40 <= rsi <= 60:
            analyses.append("RSI dengede")

        # Hacim yorumu
        if volume_ratio > 1.5:
            analyses.append("Yüksek işlem hacmi")

        return " • ".join(analyses) if analyses else "Normal seyir"

    def _get_stock_name(self, symbol: str) -> str:
        """Hisse sembolüne göre isim döndürür"""
        names = {
            "THYAO": "Türk Hava Yolları",
            "GARAN": "Garanti BBVA",
            "EREGL": "Ereğli Demir Çelik",
            "ASELS": "Aselsan",
            "KCHOL": "Koç Holding",
            "TUPRS": "Tüpraş",
            "SASA": "Sasa Polyester",
            "PGSUS": "Pegasus",
            "TAVHL": "TAV Havalimanları",
            "BIMAS": "BİM Mağazalar",
            "SAHOL": "Sabancı Holding",
            "YKBNK": "Yapı Kredi",
            "AKBNK": "Akbank",
            "ISCTR": "İş Bankası",
            "ENKAI": "Enka İnşaat",
        }
        return names.get(symbol, symbol)

    def scan_for_rising_stocks(
        self,
        symbol_prices: Dict[str, Tuple[List[float], List[int]]],
        timeframe_hours: int = 12,
        limit: int = 10
    ) -> ScanResult:
        """
        Yükseliş potansiyeli olan hisseleri tarar.

        Args:
            symbol_prices: {sembol: (fiyatlar, hacimler)} dict
            timeframe_hours: Zaman dilimi
            limit: Döndürülecek sonuç sayısı

        Returns:
            ScanResult nesnesi
        """
        recommendations = []

        for symbol, (prices, volumes) in symbol_prices.items():
            # Hacim kontrolü
            if np.mean(volumes) < self.min_volume:
                continue

            recommendation = self.analyze_stock(symbol, prices, volumes)

            if recommendation and recommendation.score >= self.min_score:
                recommendations.append(recommendation)

        # Skora göre sırala
        recommendations.sort(key=lambda x: x.score, reverse=True)

        return ScanResult(
            stocks=recommendations[:limit],
            scan_time=datetime.now(),
            timeframe=f"{timeframe_hours}h"
        )

    def format_scan_result(self, result: ScanResult) -> str:
        """Tarama sonucunu formatla"""
        if not result.stocks:
            return (
                f"📊 <b>Yükseliş Potansiyeli Taraması</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ Belirlenen kriterlere uygun hisse bulunamadı.\n"
                f"⏰ {result.scan_time.strftime('%d.%m.%Y %H:%M')}"
            )

        stocks_text = ""
        for i, stock in enumerate(result.stocks[:10], 1):
            # Trend emoji
            trend_emojis = {
                "strong_bullish": "🟢🟢",
                "bullish": "🟢",
                "neutral": "🟡",
                "bearish": "🔴",
                "strong_bearish": "🔴🔴"
            }
            emoji = trend_emojis.get(stock.trend, "⚪")

            # Skor barı
            score_bar = "█" * int(stock.score / 10) + "░" * (10 - int(stock.score / 10))

            # Hedefler
            targets_text = ""
            for target in stock.targets:
                emoji_target = "🎯" if target.change_percent > 5 else "📈"
                targets_text += f"{emoji_target} {target.period}: {target.target_price:,.2f} TL ({target.change_percent:+.1f}%)\n    "

            # Stop loss
            stop_loss_pct = ((stock.stop_loss - stock.current_price) / stock.current_price) * 100

            stocks_text += (
                f"{i}. {emoji} <b>{stock.symbol}</b> - {stock.name}\n"
                f"   └ 💰 {stock.current_price:,.2f} TL\n"
                f"   └ 📊 Skor: {score_bar} <b>({stock.score:.0f}/100)</b>\n"
                f"   └ 💡 {stock.analysis}\n"
                f"   └ ⬆️ <b>Hedefler:</b>\n"
                f"      {targets_text.strip()}\n"
                f"   └ 🛡️ Zarar Kes: {stock.stop_loss:,.2f} TL ({stop_loss_pct:.1f}%)\n"
                f"   └ 📊 RSI: {stock.rsi:.1f} | {stock.volume_signal}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )

        message = (
            f"📈 <b>YÜKSELİŞ POTANSİYELİ + HEDEFLER</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Analiz Zamanı: {result.scan_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"🎯 Hedef: 1G=1 Gün, 1H=1 Hafta, 1A=1 Ay\n\n"
            f"{stocks_text}"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <i>Yatırım tavsiyesi DEĞİLDİR. Kendi araştırmanızı yapın.</i>"
        )

        return message


# Demo veri üreticisi
def generate_demo_data(symbols: List[str], days: int = 30) -> Dict[str, Tuple[List[float], List[int]]]:
    """Demo için rastgele veri üretir"""
    random.seed(42)
    data = {}

    for symbol in symbols:
        random.seed(hash(symbol) % 1000)
        start_price = random.uniform(30, 400)

        prices = [start_price]
        for _ in range(days):
            # Yükseliş eğilimli rastgele yürüyüş
            trend = 0.4
            volatility = random.uniform(-2.5, 3)
            change = trend + volatility
            prices.append(prices[-1] * (1 + change / 100))

        base_volume = random.randint(5000000, 50000000)
        volumes = [int(base_volume * random.uniform(0.5, 2.5)) for _ in range(days)]

        data[symbol] = (prices, volumes)

    return data


# Test
if __name__ == "__main__":
    symbols = ["THYAO", "GARAN", "EREGL", "ASELS", "KCHOL", "TUPRS", "SASA", "PGSUS", "SAHOL", "BIMAS"]
    demo_data = generate_demo_data(symbols, days=30)

    screener = StockScreener()
    result = screener.scan_for_rising_stocks(demo_data, timeframe_hours=12)

    print(screener.format_scan_result(result))
