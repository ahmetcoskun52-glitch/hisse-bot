import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot aktif!\n\nKomutlar:\n/analiz THYAO\n/yukselenler"
    )

async def analiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: /analiz THYAO")
        return

    symbol = context.args[0].upper()

    # Demo analiz
    await update.message.reply_text(
        f"📊 {symbol} analiz:\nTrend: YÜKSELİŞ\nRSI: 62\nHedef: +3%"
    )

async def yukselenler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Potansiyel hisseler:\nTHYAO\nGARAN\nASELS"
    )

# --- BOT ---

def main():
    TOKEN = os.getenv("TOKEN")

    if not TOKEN:
        print("❌ TOKEN yok!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analiz", analiz))
    app.add_handler(CommandHandler("yukselenler", yukselenler))

    print("🚀 Bot başlatıldı")
    app.run_polling()

if __name__ == "__main__":
    main()
