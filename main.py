from stock_screener import StockScreener
import time

scanner = StockScreener()

while True:
    scanner.scan()
    time.sleep(60)  # 1 dakika