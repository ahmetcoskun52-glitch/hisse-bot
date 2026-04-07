def run_backtest(data):
    balance = 10000
    position = None
    trades = []

    for i in range(20, len(data)):
        price = data["Close"].iloc[i]
        high = data["High"].iloc[i-20:i].max()

        if position is None and price > high:
            position = price

        elif position:
            change = (price - position) / position * 100

            if change >= 3 or change <= -3:
                balance *= (1 + change / 100)
                trades.append(change)
                position = None

    wins = len([t for t in trades if t > 0])
    total = len(trades)

    return {
        "total": total,
        "wins": wins,
        "loss": total - wins,
        "winrate": round((wins / total) * 100, 2) if total else 0
    }