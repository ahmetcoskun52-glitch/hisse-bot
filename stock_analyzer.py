"""
Hisse Senedi Teknik Analiz Modülü
Destek/Direnç seviyeleri ve trend analizi
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SupportResistance:
    """Destek ve Direnç seviyesi"""
    level: float
    strength: float  # 0-100 arası güç
    touches: int  # Kaç kez teste edilmiş
    level_type: str  # "support" veya "resistance"


@dataclass
class TrendAnalysis:
    """Trend analiz sonucu"""
    trend: str  # "bullish", "bearish", "neutral"
    strength: float  # 0-100 arası güç
    current_price: float
    support_levels: List[SupportResistance]
    resistance_levels: List[SupportResistance]
    signals: List[str]


class StockAnalyzer:
    """
    Hisse senedi teknik analiz sınıfı

    Kullanım:
        analyzer = StockAnalyzer()
        analysis = analyzer.analyze(prices=[...], dates=[...])
    """

    def __init__(self):
        self.min_touches = 2  # Destek/direnç için minimum dokunuş sayısı

    def find_support_resistance(
        self,
        prices: List[float],
        window: int = 20,
        tolerance: float = 0.02
    ) -> Tuple[List[SupportResistance], List[SupportResistance]]:
        """
        Destek ve direnç seviyelerini bulur.

        Args:
            prices: Fiyat listesi
            window: Local ekstremum bulma penceresi
            tolerance: Yakınlık toleransı (yüzde)

        Returns:
            (destek_listesi, direnc_listesi)
        """
        prices_array = np.array(prices)
        supports = []
        resistances = []

        # Local minima (destek) ve maxima (direnç) bulma
        for i in range(window, len(prices_array) - window):
            window_prices = prices_array[i-window:i+window+1]
            current = prices_array[i]

            # Local minimum (destek)
            if current == min(window_prices):
                level = float(current)
                touches = self._count_touches(prices_array, level, tolerance)

                if touches >= self.min_touches:
                    strength = min(touches * 15, 100)
                    supports.append(SupportResistance(
                        level=level,
                        strength=strength,
                        touches=touches,
                        level_type="support"
                    ))

            # Local maximum (direnç)
            if current == max(window_prices):
                level = float(current)
                touches = self._count_touches(prices_array, level, tolerance)

                if touches >= self.min_touches:
                    strength = min(touches * 15, 100)
                    resistances.append(SupportResistance(
                        level=level,
                        strength=strength,
                        touches=touches,
                        level_type="resistance"
                    ))

        # Benzer seviyeleri birleştir
        supports = self._merge_nearby_levels(supports, tolerance)
        resistances = self._merge_nearby_levels(resistances, tolerance)

        # Güç sırasına göre sırala
        supports.sort(key=lambda x: x.strength, reverse=True)
        resistances.sort(key=lambda x: x.strength, reverse=True)

        return supports[:5], resistances[:5]  # En güçlü 5 seviye

    def _count_touches(
        self,
        prices: np.ndarray,
        level: float,
        tolerance: float
    ) -> int:
        """Belirli bir seviyenin kaç kez test edildiğini sayar"""
        touches = 0
        for price in prices:
            if abs(price - level) / level <= tolerance:
                touches += 1
        return touches

    def _merge_nearby_levels(
        self,
        levels: List[SupportResistance],
        tolerance: float
    ) -> List[SupportResistance]:
        """Yakın seviyeleri birleştirir"""
        if not levels:
            return []

        merged = []
        current = levels[0]

        for level in levels[1:]:
            if abs(level.level - current.level) / current.level <= tolerance:
                # Ortalama al ve güçleri birleştir
                total_strength = current.strength + level.strength
                current = SupportResistance(
                    level=(current.level * current.touches + level.level * level.touches) / (current.touches + level.touches),
                    strength=min(total_strength, 100),
                    touches=current.touches + level.touches,
                    level_type=current.level_type
                )
            else:
                merged.append(current)
                current = level

        merged.append(current)
        return merged

    def calculate_trend(
        self,
        prices: List[float],
        short_window: int = 10,
        long_window: int = 30
    ) -> Tuple[str, float]:
        """
        Trend yönünü ve gücünü hesaplar.

        Args:
            prices: Fiyat listesi
            short_window: Kısa vadeli hareketli ortalama
            long_window: Uzun vadeli hareketli ortalama

        Returns:
            (trend_adi, trend_gucu)
        """
        if len(prices) < long_window:
            return "neutral", 0

        prices_array = np.array(prices)

        # Hareketli ortalamalar
        short_ma = self._moving_average(prices_array, short_window)
        long_ma = self._moving_average(prices_array, long_window)

        # Son değerler
        current_price = prices[-1]
        current_short_ma = short_ma[-1] if len(short_ma) > 0 else current_price
        current_long_ma = long_ma[-1] if len(long_ma) > 0 else current_price

        # Fiyat değişim yüzdesi
        price_change = ((current_price - prices[0]) / prices[0]) * 100

        # Trend belirleme
        if current_short_ma > current_long_ma and current_price > current_short_ma:
            trend = "bullish"
            strength = min(abs(price_change) * 3, 100)
        elif current_short_ma < current_long_ma and current_price < current_short_ma:
            trend = "bearish"
            strength = min(abs(price_change) * 3, 100)
        else:
            trend = "neutral"
            strength = 50

        return trend, strength

    def _moving_average(self, prices: np.ndarray, window: int) -> np.ndarray:
        """Hareketli ortalama hesaplar"""
        if len(prices) < window:
            return np.array([])
        return np.convolve(prices, np.ones(window)/window, mode='valid')

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        RSI (Relative Strength Index) hesaplar.

        Returns:
            RSI değeri (0-100)
        """
        if len(prices) < period + 1:
            return 50

        prices_array = np.array(prices)
        deltas = np.diff(prices_array)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    def calculate_volatility(self, prices: List[float]) -> float:
        """Volatilite (standart sapma) hesaplar"""
        if len(prices) < 2:
            return 0
        return float(np.std(prices))

    def calculate_momentum(self, prices: List[float], period: int = 10) -> float:
        """Momentum hesaplar"""
        if len(prices) < period + 1:
            return 0
        return float(prices[-1] - prices[-period-1])

    def analyze(self, prices: List[float]) -> TrendAnalysis:
        """
        Kapsamlı teknik analiz yapar.

        Args:
            prices: Fiyat listesi

        Returns:
            TrendAnalysis nesnesi
        """
        current_price = prices[-1] if prices else 0

        # Destek ve direnç
        support_levels, resistance_levels = self.find_support_resistance(prices)

        # Trend analizi
        trend, strength = self.calculate_trend(prices)

        # RSI
        rsi = self.calculate_rsi(prices)

        # Momentum
        momentum = self.calculate_momentum(prices)

        # Sinyaller oluştur
        signals = []

        if rsi > 70:
            signals.append("⚠️ Aşırı alım bölgesi (RSI: {:.1f})".format(rsi))
        elif rsi < 30:
            signals.append("⚠️ Aşırı satım bölgesi (RSI: {:.1f})".format(rsi))

        if momentum > 0:
            signals.append("📈 Pozitif momentum")
        elif momentum < 0:
            signals.append("📉 Negatif momentum")

        # Trend'e göre sinyal
        if trend == "bullish":
            signals.append("🟢 Yükseliş trendinde")
        elif trend == "bearish":
            signals.append("🔴 Düşüş trendinde")

        return TrendAnalysis(
            trend=trend,
            strength=strength,
            current_price=current_price,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            signals=signals
        )

    def format_analysis_message(
        self,
        symbol: str,
        analysis: TrendAnalysis,
        exchange: str = "BIST"
    ) -> str:
        """Analiz sonucunu Telegram mesajı olarak formatlar"""

        emoji = {
            "bullish": "🟢",
            "bearish": "🔴",
            "neutral": "🟡"
        }

        trend_emoji = emoji.get(analysis.trend, "⚪")

        # Destek seviyeleri
        support_text = ""
        if analysis.support_levels:
            support_text = "\n🟢 <b>Destek Seviyeleri:</b>\n"
            for s in analysis.support_levels[:3]:
                strength_bar = "█" * int(s.strength / 20)
                support_text += f"  └ {s.level:,.2f} TL {strength_bar} ({s.touches}x test)\n"
        else:
            support_text = "\n🟢 <b>Destek Seviyeleri:</b>\n  └ Bulunamadı\n"

        # Direnç seviyeleri
        resistance_text = ""
        if analysis.resistance_levels:
            resistance_text = "\n🔴 <b>Direnç Seviyeleri:</b>\n"
            for r in analysis.resistance_levels[:3]:
                strength_bar = "█" * int(r.strength / 20)
                resistance_text += f"  └ {r.level:,.2f} TL {strength_bar} ({r.touches}x test)\n"
        else:
            resistance_text = "\n🔴 <b>Direnç Seviyeleri:</b>\n  └ Bulunamadı\n"

        # Sinyaller
        signals_text = ""
        if analysis.signals:
            signals_text = "\n📊 <b>Sinyaller:</b>\n"
            for signal in analysis.signals[:4]:
                signals_text += f"  • {signal}\n"

        message = (
            f"📈 <b>{exchange}:{symbol}</b> Analizi\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Fiyat:</b> {analysis.current_price:,.2f} TL\n"
            f"{trend_emoji} <b>Trend:</b> {analysis.trend.upper()} ({analysis.strength:.0f}% güç)\n"
            f"{support_text}"
            f"{resistance_text}"
            f"{signals_text}"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        return message


# Test
if __name__ == "__main__":
    import random
    random.seed(42)

    # Örnek fiyat verisi (100 gün)
    prices = [100]
    for i in range(99):
        change = random.uniform(-2, 2)
        prices.append(prices[-1] * (1 + change/100))

    analyzer = StockAnalyzer()
    analysis = analyzer.analyze(prices)

    print(analyzer.format_analysis_message("THYAO", analysis))
