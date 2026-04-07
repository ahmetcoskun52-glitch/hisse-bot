import os
from telegram_bot import run_bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise Exception("TOKEN YOK!")

run_bot(TOKEN)