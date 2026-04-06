"""
Telegram Bot Kurulum ve Çalıştırma Scripti
"""

import os
import sys


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


def check_env_file():
    """Environment dosyasını kontrol eder"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("⚠️ .env dosyası bulunamadı, .env.example kopyalanıyor...")
            with open(".env.example", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("✅ .env dosyası oluşturuldu")
            print("📝 Lütfen .env dosyasını düzenleyip TELEGRAM_BOT_TOKEN'ı ayarlayın")
            return False
        else:
            print("⚠️ .env.example bulunamadı")
            return False

    # Token kontrolü
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN ayarlanmamış!")
        print("📝 Lütfen .env dosyasını düzenleyin:")
        print("   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...")
        return False

    return True


def main():
    """Ana kurulum kontrolü"""
    print("🔧 Telegram Bot Kurulum Kontrolü\n")

    if not check_dependencies():
        sys.exit(1)

    if not check_env_file():
        sys.exit(1)

    print("\n🚀 Bot başlatılıyor...")
    from telegram_bot import run_bot
    from dotenv import load_dotenv

    load_dotenv()
    run_bot(os.getenv("TELEGRAM_BOT_TOKEN"))


if __name__ == "__main__":
    main()
