from http.server import BaseHTTPRequestHandler
import json
import os
import requests


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except:
            data = {}

        user_input = data.get('text', '').strip()
        if not user_input:
            self._send(400, {'error': 'Пустой запрос'})
            return

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
                    'temperature': 0.7,
                },
                timeout=25,
            )
            result = r.json()
            text = result['choices'][0]['message']['content']
            self._send(200, {'result': text})
        except Exception as e:
            self._send(500, {'error': str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
