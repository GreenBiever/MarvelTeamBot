import sqlite3 as sq
import random

db = sq.connect('Marvel.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id INTEGER,"
                "user_name TEXT,"
                "balance INTEGER,"
                "discount INTEGER,"
                "message_id INTEGER,"
                "status TEXT,"
                "notifications INTEGER)")
    db.commit()


async def cmd_start_db(user_id, user_name):
    print(user_id)
    user = cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
    print(user)
    if not user:
        return None
    else:
        return user


async def add_user(user_id, user_name):
    cur.execute(
        "INSERT INTO users (user_id, user_name, balance, discount, status, notifications) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, user_name, 0, 0, "active", 0)).fetchall()
    db.commit()


async def get_user_info(user_id):
    user = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
    if user:
        user_info = user
        return user_info
    else:
        return None


async def get_user_status(user_id):
    status = cur.execute("SELECT status FROM users WHERE user_id = ?", (user_id,)).fetchall()
    if status:
        for status in status:
            normal_status = status[0]
            return normal_status