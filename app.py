import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# Render 환경 변수에서 가져오는 값들
TELEGRAM_TOKEN = os.getenv("BOT_KEY")
OPENAI_KEY = os.getenv("EX_GPT")

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_KEY)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send_message(chat_id, text):
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    requests.post(TELEGRAM_API_URL, json=data)


def generate_reply(user_message: str) -> str:
    """
    이 함수가 실제로 GPT에 물어보고 답변 받아오는 부분
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # 사용 가능한 가벼운 모델
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 이별 상담을 해주는 따뜻하지만 솔직한 상담사야. "
                        "말투는 편한 반말, 가끔 이모지 써도 돼. "
                        "상대가 힘들어할수록 더 차분하게 공감해 줘."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )
        answer = completion.choices[0].message.content.strip()
        return answer
    except Exception as e:
        # 여기 출력이 Render 로그에 찍힘 → 디버깅용
        print("OPENAI_ERROR:", e, flush=True)
        return "지금 상담 서버에 잠깐 문제가 생겼어. 조금 있다가 다시 시도해 줘 🙏"


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" not in data:
        return "no message", 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    reply = generate_reply(text)
    send_message(chat_id, reply)

    return "ok", 200


if __name__ == "__main__":
    # 로컬 테스트용 (Render에서는 무시해도 됨)
    app.run(host="0.0.0.0", port=10000)
