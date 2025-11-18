import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("BOT_KEY")
OPENAI_KEY = os.getenv("EX_GPT")


def send_message(chat_id, text):
    """텔레그램으로 메시지 보내기 + 응답 로그 찍기"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        print("TELEGRAM_RESPONSE", r.status_code, r.text)
    except Exception as e:
        print("TELEGRAM_ERROR", repr(e))


@app.route("/", methods=["GET"])
def home():
    return "Telegram breakup bot is running!", 200


@app.route("/", methods=["POST"])
def webhook():
    """텔레그램 웹훅 엔드포인트"""
    data = request.get_json(silent=True) or {}
    print("INCOMING_UPDATE", data)  # 🔥 들어온 텔레그램 데이터 로그로 찍기

    message = data.get("message")
    if not message:
        print("NO_MESSAGE_FIELD")
        return "no message", 200

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    # 🔥 OpenAI API 직접 호출 (openai 라이브러리 안 씀)
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "너는 이별 전문 상담 AI야. "
                    "상대의 감정을 공감해 주고, 너무 가볍지 않게 "
                    "현실적인 조언을 한국어 존댓말로 해 줘."
                ),
            },
            {"role": "user", "content": user_text},
        ],
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )
        r.raise_for_status()
        res_json = r.json()
        reply = res_json["choices"][0]["message"]["content"]
    except Exception as e:
        print("OPENAI_ERROR", repr(e))
        reply = "지금 상담 서버에 잠깐 문제가 생겼어요. 조금 있다가 다시 시도해 주세요 🙏"

    send_message(chat_id, reply)
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
