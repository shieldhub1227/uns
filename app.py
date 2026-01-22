from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return "API is running", 200


@app.route("/get_id", methods=["GET"])
def get_id():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    # 기존 유저 확인
    cur.execute(
        "SELECT unique_number FROM users WHERE roblox_username = %s",
        (username,)
    )
    row = cur.fetchone()

    if row:
        number = row[0]
    else:
        # 없으면 자동 생성
        cur.execute(
            """
            INSERT INTO users (roblox_username)
            VALUES (%s)
            RETURNING unique_number
            """,
            (username,)
        )
        number = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "username": username,
        "id": number
    })


@app.route("/register_id", methods=["POST"])
def register_id():
    data = request.json
    username = data.get("username")
    number = data.get("id")

    if not username or not number:
        return jsonify({"error": "invalid data"}), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (roblox_username, unique_number)
        VALUES (%s, %s)
        ON CONFLICT (roblox_username)
        DO UPDATE SET unique_number = EXCLUDED.unique_number
        """,
        (username, number)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
