import numpy as np
from ml_model import MLModel

class StockAnalyzer:

    def __init__(self):
        self.ml = MLModel()

    def analyze(self, prices, volumes):

        prices = np.array(prices)
        volumes = np.array(volumes)

        # RSI
        delta = np.diff(prices)
        gain = np.maximum(delta, 0)
        loss = -np.minimum(delta, 0)

        avg_gain = np.mean(gain[-14:])
        avg_loss = np.mean(loss[-14:]) + 1e-6
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Trend
        trend = "BULLISH" if prices[-1] > np.mean(prices[-20:]) else "BEARISH"

        # Volume spike
        vol_avg = np.mean(volumes[-20:])
        volume_spike = volumes[-1] > vol_avg * 2

        # ML
        ml_signal = self.ml.predict(prices)

        # Support / Resistance
        support = min(prices[-20:])
        resistance = max(prices[-20:])

        breakout = prices[-1] > resistance * 0.99

        target = prices[-1] * 1.05
        stop = prices[-1] * 0.95

        score = 0
        if rsi < 70: score += 20
        if trend == "BULLISH": score += 25
        if breakout: score += 20
        if volume_spike: score += 20
        if ml_signal == "BUY": score += 15

        return {
            "price": prices[-1],
            "rsi": rsi,
            "trend": trend,
            "volume_spike": volume_spike,
            "ml": ml_signal,
            "support": support,
            "resistance": resistance,
            "target": target,
            "stop": stop,
            "score": score,
            "breakout": breakout
        }