from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import threading
from flask_cors import CORS  # type: ignore
import json
import os

app = Flask(__name__)
CORS(app)

auth_data = {}
DATA_FILE = 'ids.json'

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    username = data.get('username')
    code = data.get('code')

    if not username or not code:
        return "Bad Request", 400

    auth_data[code] = {
        "username": username,
        "timestamp": datetime.now()
    }
    print(f"[VERIFY] 저장된 코드: {code} / 현재 auth_data: {list(auth_data.keys())}")
    return "OK"

@app.route('/get_user_by_code/<code>', methods=['GET'])
def get_user_by_code(code):
    print(f"[GET_USER] 요청 코드: {code} / 저장된 코드들: {list(auth_data.keys())}")
    info = auth_data.get(code)
    if info:
        return jsonify({"username": info["username"]})
    return jsonify({}), 404

@app.route("/get_id_by_username")
def get_id_by_username():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "No username provided"}), 400

    with open("ids.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for unique_id, entry in data.items():
        if entry["roblox_username"].lower() == username.lower():
            return jsonify({"unique_id": unique_id})

    return jsonify({"error": "User not found"}), 404


@app.route('/ids.json', methods=['GET'])
def get_ids():
    if not os.path.exists(DATA_FILE):
        return jsonify([]), 200

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data), 200

def cleanup():
    while True:
        now = datetime.now()
        expired = [code for code, info in auth_data.items() if now - info["timestamp"] > timedelta(minutes=1)]
        for code in expired:
            del auth_data[code]
        threading.Event().wait(10)

threading.Thread(target=cleanup, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
