import sqlite3 as sq
import random

db = sq.connect('nft.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id INTEGER,"
                "user_name TEXT,"
                "language TEXT,"
                "balance INTEGER,"
                "message_id INTEGER,"
                "status TEXT,"
                "verification TEXT)")
    db.commit()


async def cmd_start_db(user_id, user_name):
    user = cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        return None
    else:
        return user


async def add_user(user_id, user_name, language):
    cur.execute(
        "INSERT INTO users (user_id, user_name, language, balance, status, verification) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, user_name, language, 0, "new", 0)).fetchall()
    db.commit()


async def get_user_language(user_id):
    language = (cur.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone())[0]
    if language:
        return language
    else:
        return None


async def get_user_info(user_id):
    user = (cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall())[0]
    if user:
        return user
    else:
        return None


async def get_user_status(user_id):
    status = cur.execute("SELECT status FROM users WHERE user_id = ?", (user_id,)).fetchall()
    if status:
        for status in status:
            normal_status = status[0]
            return normal_status
