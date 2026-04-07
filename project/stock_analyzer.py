import numpy as np
from ml_model import MLModel

class StockAnalyzer:

    def __init__(self):
        self.ml = MLModel()

    def analyze(self, prices, volumes):

        prices = np.array(prices)
        volumes = np.array(volumes)

        delta = np.diff(prices)
        gain = np.maximum(delta, 0)
        loss = -np.minimum(delta, 0)

        rsi = 100 - (100 / (1 + (np.mean(gain[-14:]) / (np.mean(loss[-14:]) + 1e-6))))

        trend = "YÜKSELİŞ" if prices[-1] > np.mean(prices[-20:]) else "DÜŞÜŞ"

        vol_avg = np.mean(volumes[-20:])
        volume_spike = volumes[-1] > vol_avg * 2

        ml_signal = self.ml.predict(prices)

        support = min(prices[-20:])
        resistance = max(prices[-20:])

        breakout = prices[-1] > resistance * 0.99

        target = prices[-1] * 1.05
        stop = prices[-1] * 0.95

        score = 0
        if rsi < 70: score += 20
        if trend == "YÜKSELİŞ": score += 25
        if breakout: score += 20
        if volume_spike: score += 20
        if ml_signal == "AL": score += 15

        return {
            "price": prices[-1],
            "trend": trend,
            "ml": ml_signal,
            "score": score,
            "target": target,
            "stop": stop,
            "volume_spike": volume_spike,
            "breakout": breakout
        }