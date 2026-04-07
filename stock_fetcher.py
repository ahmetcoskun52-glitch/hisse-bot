import yfinance as yf

def get_stock_data(symbol):
    try:
        data = yf.Ticker(symbol + ".IS").history(period="5d", interval="15m")

        if data.empty:
            return None, None

        return data["Close"].tolist(), data["Volume"].tolist()
    except:
        return None, None