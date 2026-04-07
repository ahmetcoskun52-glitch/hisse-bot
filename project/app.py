@app.route("/stock/<symbol>")
def stock_detail(symbol):
    from data_fetcher import get_stock_data
    from stock_analyzer import StockAnalyzer

    ohlc, prices, volumes = get_stock_data(symbol)

    analyzer = StockAnalyzer()
    data = analyzer.analyze(prices, volumes)

    return render_template(
        "detail.html",
        symbol=symbol,
        ohlc=ohlc,
        prices=prices,
        data=data
    )