from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Sefaria Note API is running!"

@app.route('/send_note', methods=['POST'])
def send_note():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
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
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }

    login_data = {
        'email': email,
        'password': password
    }

    resp2 = session.post('https://www.sefaria.org.il/api/login', json=login_data, headers=headers)

    if resp2.status_code != 200 or 'user' not in resp2.json():
        return jsonify({'error': 'Login failed', 'response': resp2.text}), 401

    # Step 3: send note
    note_data = {
        "json": {
            "text": text,
            "refs": [ref],
            "type": "note",
            "public": False
        }
    }

    headers_note = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf_token
    }

    response = session.post("https://www.sefaria.org.il/api/notes/", data={"json": requests.utils.json.dumps(note_data["json"])}, headers=headers_note)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to send note', 'response': response.text}), 400

    return jsonify({'success': True, 'result': response.json()}), 200

# ✅ listen on the correct port!
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # use Render's port
    app.run(host='0.0.0.0', port=port)
