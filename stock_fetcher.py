import yfinance as yf
import time

CACHE = {}
CACHE_TTL = 60  # saniye

def get_stock_data(symbol):
    now = time.time()

    if symbol in CACHE:
        data, ts = CACHE[symbol]
        if now - ts < CACHE_TTL:
            return data

    try:
        stock = yf.Ticker(symbol + ".IS")
        data = stock.history(period="5d", interval="15m")

        if data.empty:
            return None

        CACHE[symbol] = (data, now)
        return data
    except:
        return None


def get_current_price(symbol):
    data = get_stock_data(symbol)
    if data is None:
        return None
    return data["Close"].iloc[-1]