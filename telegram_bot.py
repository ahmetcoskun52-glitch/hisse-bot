import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- KOMUTLAR ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot aktif!\n\n"
        "Komutlar:\n"
        "/analiz THYAO\n"
        "/yukselenler"
    )


async def analiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: /analiz THYAO")
        return

    symbol = context.args[0].upper()

    prices = [100, 102, 101, 105, 110, 108, 115]

    analyzer = StockAnalyzer()
    result = analyzer.analyze(prices)

    msg = analyzer.format_analysis_message(symbol, result)
    await update.message.reply_text(msg, parse_mode="HTML")


async def yukselenler_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Tarama yapılıyor...")

    symbols = ["THYAO", "GARAN", "ASELS"]

    from stock_screener import generate_demo_data
    data = generate_demo_data(symbols)

    screener = StockScreener()
    result = screener.scan_for_rising_stocks(data)

    msg = screener.format_scan_result(result)
    await update.message.reply_text(msg, parse_mode="HTML")


# --- BOT ---

def run_bot(token: str):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("analiz", analiz_command))
    app.add_handler(CommandHandler("yukselenler", yukselenler_command))

    logger.info("Bot çalışıyor...")
    app.run_polling()
