from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Sefaria Note API is running!"

@app.route('/send_note', methods=['POST'])
def send_note():
    data = request.get_json()
    
    # ✅ כתוב כאן את שם המשתמש והסיסמה שלך (אופציה זמנית):
    email = "davidpovarski1@gmail.com"
    password = "sefaria"

    # שדות מהבקשה
    ref = data.get('ref')
    text = data.get('text')

    if not all([email, password, ref, text]):
        return jsonify({'error': 'Missing fields'}), 400

    session = requests.Session()

    # Step 1: get CSRF token
    resp1 = session.get('https://www.sefaria.org.il/login')
    csrf_token = session.cookies.get('csrftoken')

    if not csrf_token:
        return jsonify({'error': 'CSRF token not found'}), 500

    # Step 2: log in
    headers = {
        'Referer': 'https://www.sefaria.org.il/login',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrf_token,
        'User-Agent': 'Mozilla/5.0'
    }

    login_data = {
        'email': email,
        'password': password
    }

    resp2 = session.post('https://www.sefaria.org.il/login', data=login_data, headers=headers)

try:
    login_json = resp2.json()
except ValueError:
    return jsonify({'error': 'Login failed - response not JSON', 'response': resp2.text}), 500

if resp2.status_code != 200 or 'user' not in login_json:
    return jsonify({'error': 'Login failed', 'response': login_json}), 401
    # Step 3: send note
    note_data = {
        "text": text,
        "refs": [ref],
        "type": "note",
        "public": False
    }

    headers_note = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf_token,
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.sefaria.org.il/"
    }

    response = session.post(
        "https://www.sefaria.org.il/api/notes/",
        data={"json": json.dumps(note_data)},
        headers=headers_note
    )

    if response.status_code != 200:
        return jsonify({'error': 'Failed to send note', 'response': response.text}), 400

    return jsonify({'success': True, 'result': response.json()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)