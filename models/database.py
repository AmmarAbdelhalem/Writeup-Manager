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
            status TEXT DEFAULT 'Unreaded'
        );
        """
        self.conn.execute(query)
        self.conn.commit()
        
        # Add status column to existing tables if it doesn't exist
        try:
            self.conn.execute("ALTER TABLE writeups ADD COLUMN status TEXT DEFAULT 'Unreaded'")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

    def add_writeup(self, title, category, url):
        query = """
        INSERT INTO writeups (title, category, url, status)
        VALUES (?, ?, ?, 'Unreaded');
        """
        cursor = self.conn.execute(query, (title, category, url))
        self.conn.commit()
        return cursor.lastrowid
    
    def writeups_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, category, url, status FROM writeups ORDER BY title")
        rows = cur.fetchall()
        return rows

    def search(self, query: str):
        like = f"%{query}%"
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, title, category, url, status FROM writeups WHERE title LIKE ? ORDER BY title",
            (like,)
        )
        rows = cur.fetchall()
        return rows
    
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
    
    def mark_as_readed(self, writeup_id):
        query = """
        UPDATE writeups
        SET status = 'Readed'
        WHERE id = ?;
        """
        self.conn.execute(query, (writeup_id,))
        self.conn.commit()
        
    def mark_as_unreaded(self, writeup_id):
        query = """
        UPDATE writeups
        SET status = 'Unreaded'
        WHERE id = ?;
        """
        self.conn.execute(query, (writeup_id,))
        self.conn.commit()
    
    def get_all_categories(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT category FROM writeups ORDER BY category")
        rows = cur.fetchall()
        return [row[0] for row in rows]
    
    def filter_by_category(self, category):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, category, url, status FROM writeups WHERE category = ? ORDER BY title", (category,))
        rows = cur.fetchall()
        return rows
    
    def filter_by_status(self, status):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, category, url, status FROM writeups WHERE status = ? ORDER BY title", (status,))
        rows = cur.fetchall()
        return rows
    
    def filter_by_category_and_status(self, category, status):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, category, url, status FROM writeups WHERE category = ? AND status = ? ORDER BY title", (category, status))
        rows = cur.fetchall()
        return rows

    def close(self):
        self.conn.close()