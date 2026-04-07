from flask import Flask, render_template, jsonify
from stock_screener import StockScreener
import requests

app = Flask(__name__)
scanner = StockScreener()

# 🔐 TOKEN BURAYA
BOT_TOKEN = "BURAYA_YENI_TOKEN"
CHAT_ID = "8632093232:AAHg9bG1JWjgWe6EUDaecegGaixpajJIdJk"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


@app.route("/")
def home():
    results, _ = scanner.scan_web()
    return render_template("index.html", results=results)


@app.route("/scan")
def scan():
    results, alerts = scanner.scan_web()

    # 🔔 TELEGRAM GÖNDER
    for a in alerts:
        send_telegram(
            f"🚀 {a['symbol']} AL sinyali!\n"
            f"Skor: {a['score']}"
        )

    return jsonify({"results": results, "alerts": alerts})


if __name__ == "__main__":
    app.run(debug=True)