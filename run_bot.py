import os
from telegram_bot import run_bot

token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    raise Exception("TOKEN YOK")

run_bot(token)