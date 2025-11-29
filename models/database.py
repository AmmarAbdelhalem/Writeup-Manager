import sqlite3
from datetime import datetime

class Database:
    def __init__(self, path="writeups.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS writeups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            url TEXT,
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_writeup(self, title, category, url):
        query = """
        INSERT INTO writeups (title, category, url)
        VALUES (?, ?, ?);
        """
        cursor = self.conn.execute(query, (title, category, url))
        self.conn.commit()
        return cursor.lastrowid

    def get_writeups(self):
        cursor = self.conn.execute("SELECT * FROM writeups ORDER BY id DESC;")
        return [dict(row) for row in cursor.fetchall()]

    def get_writeup_by_id(self, writeup_id):
        cursor = self.conn.execute("SELECT * FROM writeups WHERE id = ?;", (writeup_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_writeup(self, writeup_id, title, category, url):
        query = """
        UPDATE writeups
        SET title = ?, category = ?, url = ?
        WHERE id = ?;
        """
        self.conn.execute(query, (title, category, url, writeup_id))
        self.conn.commit()

    def delete_writeup(self, writeup_id):
        self.conn.execute("DELETE FROM writeups WHERE id = ?;", (writeup_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()