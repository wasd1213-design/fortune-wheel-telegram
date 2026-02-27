from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import psycopg2

# Настройки подключения к базе
DB_URL = "postgresql://bot_user:120490@localhost/bot_db"

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route('/api/is_can_spin')
def is_can_spin():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"can_spin": False, "wait_msg": "Нет user_id"}), 400
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT last_fortune_time FROM users WHERE user_id = %s", (user_id,))
                res = cur.fetchone()
                now = datetime.utcnow()
                if res and res[0]:
                    last_spin = res[0]
                    delta = now - last_spin
                    if delta < timedelta(hours=6):
                        hours_left = 5 - delta.seconds // 3600
                        mins_left = (3600 - (delta.seconds % 3600)) // 60
                        wait_msg = f"Вы сможете крутить колесо через {hours_left} ч {mins_left} мин."
                        return jsonify({"can_spin": False, "wait_msg": wait_msg})
        # Если крутили давно или не крутили — можно крутить
        return jsonify({"can_spin": True})
    except Exception as e:
        return jsonify({"can_spin": False, "wait_msg": f"Ошибка: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
