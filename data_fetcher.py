import yfinance as yf
from functools import lru_cache

@lru_cache(maxsize=100)
def get_price_history(symbol):
    data = yf.Ticker(symbol + ".IS").history(period="5d", interval="15m")

    if data.empty:
        return [100]

    return data["Close"].tolist()