from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from scanner import scan_stocks
from symbols import BIST_ALL

# -------------------
# START
# -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot aktif!\n\n"
        "/scan → hisse tarama"
    )

# -------------------
# SCAN
# -------------------
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Tarama başlıyor...")

    try:
        results = scan_stocks(BIST_ALL)

        if not results:
            await update.message.reply_text("Sinyal yok ❌")
            return

        msg = "🚀 SİNYALLER:\n\n"

        for r in results:
            msg += (
                f"{r['symbol']}\n"
                f"Fiyat: {r['price']}\n"
                f"Hedef: {r['target']}\n"
                f"Stop: {r['stop']}\n"
                f"Skor: {r['score']}\n\n"
            )

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Hata: {str(e)}")

# -------------------
# RUN
# -------------------
def run_bot(token):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("🚀 Bot çalışıyor...")
    app.run_polling()
