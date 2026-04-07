def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_score(data):
    rsi = calculate_rsi(data).iloc[-1]
    price = data["Close"].iloc[-1]

    score = 0

    if 40 < rsi < 65:
        score += 40
    if rsi < 40:
        score += 20

    return {
        "rsi": round(rsi, 2),
        "price": round(price, 2),
        "score": score
    }