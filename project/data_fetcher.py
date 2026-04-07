import yfinance as yf

def get_stock_data(symbol):
    try:
        df = yf.Ticker(symbol + ".IS").history(period="5d", interval="15m")

        if df is None or df.empty:
            return None, None, None

        ohlc = []
        closes = []
        volumes = []

        for i, row in df.iterrows():
            ohlc.append({
                "time": int(i.timestamp()),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"])
            })
            closes.append(float(row["Close"]))
            volumes.append(float(row["Volume"]))

        return ohlc, closes, volumes

    except:
        return None, None, None