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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 이별 전문 상담 AI야. 공감하면서 따뜻하게 답해."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message["content"]
        send_message(chat_id, reply)

    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "Telegram bot server running!"
