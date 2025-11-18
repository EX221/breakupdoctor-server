import os
from flask import Flask, request
import requests
from openai import OpenAI

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("BOT_KEY")
OPENAI_KEY = os.getenv("EX_GPT")

client = OpenAI(api_key=OPENAI_KEY)


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        # OpenAI 최신 버전 방식
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        ai_reply = response.choices[0].message["content"]

        send_message(chat_id, ai_reply)

    return "OK", 200


@app.route("/", methods=["GET"])
def home():
    return "Telegram bot running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
