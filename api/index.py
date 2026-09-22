from http.server import BaseHTTPRequestHandler
import json
import os
import requests


def ask_groq(prompt, temperature=0.6):
    key = os.environ.get('GROQ_KEY', '')
    r = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
        },
        json={
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': temperature,
        },
        timeout=25,
    )
    result = r.json()
    return result['choices'][0]['message']['content']


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except:
            data = {}

        user_input = data.get('text', '').strip()
        mode = data.get('mode', 'names')  # 'names' или 'analytics'

        if not user_input:
            self._send(400, {'error': 'Пустой запрос'})
            return

        if mode == 'names':
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
            temp = 0.7
        else:
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
            temp = 0.5

        try:
            text = ask_groq(prompt, temp)
            self._send(200, {'result': text})
        except Exception as e:
            self._send(500, {'error': str(e)})

    def do_GET(self):
        self._send(200, {'status': 'AiFunPay API works'})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
