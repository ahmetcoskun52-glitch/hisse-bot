import os
import sys
from telegram_bot import run_bot


def check_dependencies():
    """Bağımlılıkları kontrol eder"""
    try:
        import telegram
        import dotenv
        import numpy
        print("✅ Tüm bağımlılıklar kurulu")
        return True
    except ImportError as e:
        print(f"❌ Eksik bağımlılık: {e}")
        print("\n📦 Kurulum için:")
        print("   pip install -r requirements.txt")
        return False


def main():
    """Ana başlatma"""
    print("🚀 Bot başlatılıyor...\n")

    if not check_dependencies():
        sys.exit(1)

    # Railway environment variable direkt alınır
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN bulunamadı!")
        sys.exit(1)

    run_bot(token)


if __name__ == "__main__":
    main()
