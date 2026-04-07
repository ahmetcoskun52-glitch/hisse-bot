import os
from telegram_bot import run_bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("TOKEN YOK!")
else:
    run_bot(TOKEN)