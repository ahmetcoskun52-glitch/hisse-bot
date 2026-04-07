from data_fetcher import get_stock_data
from smart_analyzer import calculate_score
from breakout import detect_breakout
from risk_manager import calculate_trade_levels
from chart import generate_chart

def scan_stocks(symbols):
    results = []

    for s in symbols:
        data = get_stock_data(s)

        if data is None or len(data) < 30:
            continue

        if not detect_breakout(data):
            continue

        score_data = calculate_score(data)

        if score_data["score"] < 30:
            continue

        price = score_data["price"]
        target, stop = calculate_trade_levels(price)
        chart = generate_chart(data, s)

        results.append({
            "symbol": s,
            "price": price,
            "target": target,
            "stop": stop,
            "chart": chart
        })

    return results[:3]