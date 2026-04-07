from data_fetcher import get_stock_data
from stock_analyzer import StockAnalyzer
import json

class StockScreener:

    def __init__(self):
        self.symbols = [
            "THYAO","GARAN","ASELS","KCHOL","SASA","TUPRS",
            "BIMAS","SAHOL","AKBNK","EREGL","PGSUS","TCELL"
        ]
        self.cache_file = "cache.json"

    def load_cache(self):
        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except:
            return {}

    def save_cache(self, data):
        with open(self.cache_file, "w") as f:
            json.dump(data, f)

    def scan(self):
        analyzer = StockAnalyzer()
        cache = self.load_cache()
        new_cache = {}

        print("\n🚀 TARAMA BAŞLADI\n")

        for s in self.symbols:
            prices, volumes = get_stock_data(s)

            if not prices:
                continue

            result = analyzer.analyze(prices, volumes)

            key = f"{s}_{result['trend']}"

            # tekrar engelle
            if cache.get(s) == key:
                continue

            new_cache[s] = key

            if result["score"] > 70:
                print(f"""
🟢 {s}
Skor: {result['score']}
Trend: {result['trend']}
ML: {result['ml']}
RSI: {result['rsi']:.1f}

🎯 {result['target']:.2f}
🛑 {result['stop']:.2f}

{'🚀 BREAKOUT' if result['breakout'] else ''}
{'📊 HACİM' if result['volume_spike'] else ''}
""")

        self.save_cache(new_cache)