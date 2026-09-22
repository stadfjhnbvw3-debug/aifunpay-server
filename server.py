from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # разрешаем запросы с любых устройств

# ВСТАВЬ СВОЙ КЛЮЧ GROQ ЗДЕСЬ (между кавычками)
import os
GROQ_KEY = os.environ.get("GROQ_KEY", "")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


@app.route("/", methods=["GET"])
def home():
    return "AiFunPay Server is running ✅"


@app.route("/api/names", methods=["POST"])
def generate_names():
    """Генерация названия, описания, автовыдачи"""
    data = request.get_json()
    user_input = data.get("text", "").strip()
    if not user_input:
        return jsonify({"error": "Пустой запрос"}), 400

    prompt = f"""Ты помощник продавца на FunPay. Пользователь описал товар: "{user_input}"

Сгенерируй для лота на FunPay:
1. НАЗВАНИЕ (до 60 символов, с эмодзи, цепляющее)
2. ОПИСАНИЕ (3-5 предложений, что входит, условия)
3. АВТОВЫДАЧА (короткое сообщение покупателю после оплаты)

Отвечай строго в формате:
НАЗВАНИЕ: ...
ОПИСАНИЕ: ...
АВТОВЫДАЧА: ...
"""

    try:
        r = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
            timeout=30,
        )
        result = r.json()
        text = result["choices"][0]["message"]["content"]
        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics", methods=["POST"])
def analytics():
    """Аналитика цены и спроса"""
    data = request.get_json()
    user_input = data.get("text", "").strip()
    if not user_input:
        return jsonify({"error": "Пустой запрос"}), 400

    prompt = f"""Ты аналитик рынка FunPay. Пользователь хочет продать: "{user_input}"

Дай оценку в рублях:
1. РЕКОМЕНДУЕМАЯ ЦЕНА (одно число в ₽)
2. ВИЛКА ЦЕН (мин - макс в ₽)
3. СПРОС (Высокий / Средний / Низкий)
4. ТРЕНД (Растёт / Падает / Стабильно)
5. СОВЕТ (1 предложение)

Отвечай строго в формате:
ЦЕНА: ...
ВИЛКА: ...
СПРОС: ...
ТРЕНД: ...
СОВЕТ: ...
"""

    try:
        r = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
            },
            timeout=30,
        )
        result = r.json()
        text = result["choices"][0]["message"]["content"]
        return jsonify({"result": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)