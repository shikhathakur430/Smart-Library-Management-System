import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "library.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT UNIQUE,
            total_copies INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1,
            added_on TEXT DEFAULT CURRENT_DATE
        );
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            joined_on TEXT DEFAULT CURRENT_DATE
        );
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL DEFAULT CURRENT_DATE,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL DEFAULT 'Borrowed',
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(member_id) REFERENCES members(id)
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        if count == 0:
            sample_books = [
                ("Python Crash Course", "Eric Matthes", "Programming", "9781593279288", 5, 5),
                ("Clean Code", "Robert C. Martin", "Programming", "9780132350884", 3, 3),
                ("The Alchemist", "Paulo Coelho", "Fiction", "9780061122415", 4, 4),
                ("Atomic Habits", "James Clear", "Self-help", "9780735211292", 4, 4),
                ("A Brief History of Time", "Stephen Hawking", "Science", "9780553380163", 2, 2),
                ("The Pragmatic Programmer", "David Thomas", "Programming", "9780135957059", 3, 3),
                ("Wings of Fire", "A. P. J. Abdul Kalam", "Biography", "9788173711466", 3, 3),
            ]
            conn.executemany("""INSERT INTO books
                (title, author, category, isbn, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)""", sample_books)
        conn.commit()
