import os
from flask import Flask, request
import requests
from openai import OpenAI

app = Flask(__name__)

# Render 환경변수에서 가져옴
TELEGRAM_TOKEN = os.getenv("BOT_KEY")
OPENAI_KEY = os.getenv("EX_GPT")

client = OpenAI(api_key=OPENAI_KEY)


def send_message(chat_id: int, text: str):
    """텔레그램으로 메시지 보내는 함수"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    # 실패해도 서버 안 죽게 예외 무시
    try:
        requests.post(url, json=data, timeout=10)
    except Exception:
        pass


@app.route("/", methods=["GET"])
def home():
    return "Telegram breakup bot is running!", 200


@app.route("/", methods=["POST"])
def webhook():
    """텔레그램이 보내주는 메시지를 받아서 답장"""
    data = request.get_json(silent=True) or {}

    message = data.get("message")
    if not message:
        return "no message", 200

    chat_id = message["chat"]["id"]
    user_text = message.get("text") or ""

    # OpenAI에게 답변 요청
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 이별 전문 상담 AI야. "
                    "상대의 감정을 공감해 주고, 너무 훈수두는 느낌 말고 "
                    "따뜻하지만 솔직하게 이야기해 줘."
                ),
            },
            {"role": "user", "content": user_text},
        ],
    )

    reply = completion.choices[0].message.content
    send_message(chat_id, reply)

    return "ok", 200


if __name__ == "__main__":
    # 로컬 테스트용 / Render에서도 PORT 환경변수 따라감
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
