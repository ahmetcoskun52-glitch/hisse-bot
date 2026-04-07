def detect_breakout(data):
    last_price = data["Close"].iloc[-1]
    high = data["High"].rolling(20).max().iloc[-2]

    return last_price > high