import os
import sys
from telegram_bot import run_bot

def main():
    print("🚀 Bot başlatılıyor...")

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN bulunamadı!")
        sys.exit(1)

    run_bot(token)

if __name__ == "__main__":
    main()
