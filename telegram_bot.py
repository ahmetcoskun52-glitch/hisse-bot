import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener
from stock_monitor import StockMonitor
from data_fetcher import get_price_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

monitor = StockMonitor()

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Aktif!\n\n"
        "/analiz THYAO\n"
        "/tara\n"
        "/baslat"
    )

async def analiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper()

    prices = get_price_history(symbol)

    analyzer = StockAnalyzer()
    result = analyzer.analyze(prices)

    msg = analyzer.format_analysis_message(symbol, result)
    await update.message.reply_text(msg, parse_mode="HTML")

async def tara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbols = ["THYAO","GARAN","ASELS","KCHOL","SASA","TUPRS"]

    screener = StockScreener()
    results = screener.scan(symbols)

    await update.message.reply_text(results, parse_mode="HTML")

async def baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    monitor.start(chat_id)

    await update.message.reply_text("🚀 Otomatik tarama başladı!")

# --- BOT ---

def run_bot(token):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analiz", analiz))
    app.add_handler(CommandHandler("tara", tara))
    app.add_handler(CommandHandler("baslat", baslat))

    app.run_polling()