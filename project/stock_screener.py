from data_fetcher import get_stock_data
from stock_analyzer import StockAnalyzer

class StockScreener:

    def __init__(self):
        self.symbols = [
            "THYAO","GARAN","ASELS","KCHOL","SASA","TUPRS",
            "BIMAS","SAHOL","AKBNK","EREGL","PGSUS","TCELL",
            "YKBNK","TAVHL","KOZAL","ISCTR","HALKB","VAKBN"
        ]
        self.last_signals = {}

    def scan_web(self):
        analyzer = StockAnalyzer()
        results = []
        alerts = []

        for s in self.symbols:
            prices, volumes = get_stock_data(s)

            if not prices:
                continue

            data = analyzer.analyze(prices, volumes)

            key = f"{data['trend']}_{data['ml']}"

            # YENİ SİNYAL
            if self.last_signals.get(s) != key and data["score"] > 60:
                alerts.append({
                    "symbol": s,
                    "score": data["score"]
                })

            self.last_signals[s] = key

            if data["score"] > 60:
                results.append({
                    "symbol": s,
                    **data
                })

        return results, alerts