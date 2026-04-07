import asyncio
from stock_screener import StockScreener

class StockMonitor:

    def __init__(self):
        self.running = False
        self.sent = {}

    def start(self, chat_id):
        self.running = True
        asyncio.create_task(self.loop(chat_id))

    async def loop(self, chat_id):
        screener = StockScreener()
        symbols = ["THYAO","GARAN","ASELS","SASA"]

        while self.running:
            result = screener.scan(symbols)
            print(result)
            await asyncio.sleep(60)