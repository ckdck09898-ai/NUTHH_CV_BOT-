import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("nuthh_cv.sqlite3")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, language TEXT NOT NULL DEFAULT 'en', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'My CV', data_json TEXT NOT NULL,
            template_id TEXT NOT NULL DEFAULT 'professional_01', updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, title)
        )""")

def ensure_user(user_id):
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (user_id,))

def set_language(user_id, language):
    with connect() as db:
        db.execute("INSERT INTO users(user_id, language) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET language=excluded.language", (user_id, language))

def get_language(user_id):
    with connect() as db:
        row = db.execute("SELECT language FROM users WHERE user_id=?", (user_id,)).fetchone()
    return row["language"] if row else "en"

def save_cv(user_id, data, template_id, title="My CV"):
    payload = json.dumps(data, ensure_ascii=False)
    with connect() as db:
        db.execute("""INSERT INTO cvs(user_id,title,data_json,template_id,updated_at)
        VALUES(?,?,?,?,CURRENT_TIMESTAMP)
        ON CONFLICT(user_id,title) DO UPDATE SET data_json=excluded.data_json,
        template_id=excluded.template_id, updated_at=CURRENT_TIMESTAMP""",
        (user_id, title, payload, template_id))

def load_cv(user_id, title="My CV"):
    with connect() as db:
        row = db.execute("SELECT * FROM cvs WHERE user_id=? AND title=?", (user_id, title)).fetchone()
    if not row:
        return None
    result = dict(row)
    result["data"] = json.loads(result.pop("data_json"))
    return result

def list_cvs(user_id):
    with connect() as db:
        return db.execute("SELECT title,template_id,updated_at FROM cvs WHERE user_id=? ORDER BY updated_at DESC", (user_id,)).fetchall()
