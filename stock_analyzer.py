import numpy as np

class StockAnalyzer:

    def analyze(self, prices):
        prices = np.array(prices)

        delta = np.diff(prices)
        gain = np.maximum(delta, 0)
        loss = -np.minimum(delta, 0)

        avg_gain = np.mean(gain[-14:])
        avg_loss = np.mean(loss[-14:]) + 1e-6

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        ema12 = self.ema(prices, 12)
        ema26 = self.ema(prices, 26)

        macd = ema12 - ema26
        signal = self.ema(macd, 9)

        trend = "BULLISH" if prices[-1] > np.mean(prices[-20:]) else "BEARISH"

        support = min(prices[-20:])
        resistance = max(prices[-20:])

        breakout = prices[-1] > resistance * 0.99

        target = prices[-1] * 1.05
        stop = prices[-1] * 0.95

        score = 0
        if rsi < 70: score += 20
        if macd[-1] > signal[-1]: score += 30
        if trend == "BULLISH": score += 30
        if breakout: score += 20

        return {
            "price": prices[-1],
            "rsi": rsi,
            "trend": trend,
            "support": support,
            "resistance": resistance,
            "target": target,
            "stop": stop,
            "score": score,
            "breakout": breakout
        }

    def ema(self, data, period):
        ema = []
        k = 2 / (period + 1)
        for i in range(len(data)):
            if i == 0:
                ema.append(data[i])
            else:
                ema.append(data[i] * k + ema[i-1]*(1-k))
        return np.array(ema)

    def format_analysis_message(self, symbol, d):
        return f"""
📊 <b>{symbol}</b>

💰 {d['price']:.2f}
📈 {d['trend']}
📊 Skor: {d['score']}

📌 Destek: {d['support']:.2f}
📌 Direnç: {d['resistance']:.2f}

🎯 Hedef: {d['target']:.2f}
🛑 Stop: {d['stop']:.2f}

{'🚀 BREAKOUT' if d['breakout'] else ''}
"""