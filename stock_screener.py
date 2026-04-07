from stock_analyzer import StockAnalyzer
from data_fetcher import get_price_history

class StockScreener:

    def scan(self, symbols):
        analyzer = StockAnalyzer()

        results = "🚀 TARANAN HİSSELER\n\n"

        for s in symbols:
            prices = get_price_history(s)
            data = analyzer.analyze(prices)

            if data["score"] > 60:
                results += f"🟢 {s} | Skor: {data['score']}\n"

        return results