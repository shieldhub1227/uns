from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DB_FILE = "db.json"

def load_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/get_id", methods=["GET"])
def get_id():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username required"}), 400

    db = load_db()

    if username in db:
        return jsonify({
            "username": username,
            "id": db[username]
        })
    else:
        return jsonify({
            "username": username,
            "id": "UNKNOWN"
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
