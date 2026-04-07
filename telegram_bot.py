from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from scanner import scan_stocks
from data_fetcher import get_stock_data
from backtest import run_backtest

WATCHLIST = ["THYAO", "GARAN", "ASELS", "KCHOL", "TUPRS"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot aktif!")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Tarama yapılıyor...")

    results = scan_stocks(WATCHLIST)

    if not results:
        await update.message.reply_text("Sinyal yok ❌")
        return

    for r in results:
        msg = (
            f"🚀 {r['symbol']}\n"
            f"💰 {r['price']}\n"
            f"🎯 {r['target']}\n"
            f"🛑 {r['stop']}"
        )

        await update.message.reply_photo(
            photo=open(r["chart"], "rb"),
            caption=msg
        )

async def backtest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0]
    data = get_stock_data(symbol)

    result = run_backtest(data)

    await update.message.reply_text(str(result))

def run_bot(token):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("backtest", backtest_cmd))

    app.run_polling()