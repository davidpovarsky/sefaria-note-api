from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Sefaria Note API is running!"

@app.route('/send_note', methods=['POST'])
def send_note():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    ref = data.get("ref")
    note_text = data.get("text")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.sefaria.org.il/login"
    })

    # שלב 1: קבל CSRF
    login_page = session.get("https://www.sefaria.org.il/login")
    csrf_token = session.cookies.get("csrftoken")

    if not csrf_token:
        return jsonify({"error": "CSRF token not found"}), 400

    # שלב 2: התחברות
    login_data = {
        "email": email,
        "password": password,
        "csrfmiddlewaretoken": csrf_token
    }

    login_headers = {
        "Referer": "https://www.sefaria.org.il/login",
        "X-CSRFToken": csrf_token
    }

    response = session.post(
        "https://www.sefaria.org.il/login",
        data=login_data,
        headers=login_headers,
        allow_redirects=False
    )

    if response.status_code != 302:
        return jsonify({"error": "Login failed"}), 401

    # שלב 3: שליחת ההערה
    note_data = {
        "json": '{"text": "%s", "refs": ["%s"], "type": "note", "public": false}' % (note_text, ref)
    }

    note_headers = {
        "X-CSRFToken": session.cookies.get("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.sefaria.org.il/"
    }

    note_response = session.post(
        "https://www.sefaria.org.il/api/notes/",
        data=note_data,
        headers=note_headers
    )

    if note_response.ok:
        return jsonify(note_response.json())
    else:
        return jsonify({"error": "Failed to send note", "response": note_response.text}), 400
