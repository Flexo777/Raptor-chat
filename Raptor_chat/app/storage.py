import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_NAME = 'chatapp.db'

class User:
    def __init__(self, id, username, email, password, online):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.online = online

class DatabaseManager:
    def __init__(self):
        self.db_name = DB_NAME
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            online INTEGER NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message_type TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )''')
        conn.commit()
        conn.close()

    def add_user(self, username, email, password):
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (username, email, password, online)
        VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, 1))
        conn.commit()
        conn.close()

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(id=user_data[0], username=user_data[1], email=user_data[2], password=user_data[3], online=user_data[4])
        return None

    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(id=user_data[0], username=user_data[1], email=user_data[2], password=user_data[3], online=user_data[4])
        return None

    def verify_password(self, user, password):
        return check_password_hash(user.password, password)

    def update_user_status(self, user_id, online):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET online = ? WHERE id = ?', (online, user_id))
        conn.commit()
        conn.close()

    def save_message(self, sender_id, receiver_id, message_type, content, timestamp):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, message_type, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', (sender_id, receiver_id, message_type, content, timestamp))
        conn.commit()
        conn.close()

    def get_messages(self, user_id1, user_id2):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT sender_id, receiver_id, message_type, content, timestamp
        FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY datetime(timestamp)
        ''', (user_id1, user_id2, user_id2, user_id1))
        messages = cursor.fetchall()
        conn.close()

        # Format ke dict agar lebih mudah diakses di template
        formatted = [
            {
                'sender_id': m[0],
                'receiver_id': m[1],
                'type': m[2],
                'content': m[3],
                'timestamp': datetime.strptime(m[4], "%Y-%m-%d %H:%M:%S") if m[4] else None
            } for m in messages
        ]
        return formatted

    def get_online_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE online = 1')
        users_data = cursor.fetchall()
        conn.close()
        return [User(id=u[0], username=u[1], email=u[2], password=u[3], online=u[4]) for u in users_data]
