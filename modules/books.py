import pandas as pd
from database import get_connection

def get_books(search=""):
    with get_connection() as conn:
        if search:
            term = f"%{search}%"
            rows = conn.execute("""SELECT * FROM books
                WHERE title LIKE ? OR author LIKE ? OR category LIKE ? OR isbn LIKE ?
                ORDER BY title""", (term, term, term, term)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    return pd.DataFrame([dict(r) for r in rows])

def add_book(title, author, category, isbn, copies):
    with get_connection() as conn:
        conn.execute("""INSERT INTO books
            (title, author, category, isbn, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (title.strip(), author.strip(), category, isbn.strip() or None, copies, copies))
        conn.commit()

def update_book(book_id, title, author, category, isbn, total_copies):
    with get_connection() as conn:
        row = conn.execute("SELECT total_copies, available_copies FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            raise ValueError("Book not found.")
        borrowed = row["total_copies"] - row["available_copies"]
        if total_copies < borrowed:
            raise ValueError(f"At least {borrowed} copies are currently borrowed.")
        available = total_copies - borrowed
        conn.execute("""UPDATE books SET title=?, author=?, category=?, isbn=?,
            total_copies=?, available_copies=? WHERE id=?""",
            (title.strip(), author.strip(), category, isbn.strip() or None,
             total_copies, available, book_id))
        conn.commit()

def delete_book(book_id):
    with get_connection() as conn:
        active = conn.execute("SELECT COUNT(*) FROM borrowings WHERE book_id=? AND status='Borrowed'", (book_id,)).fetchone()[0]
        if active:
            raise ValueError("This book has active borrowings and cannot be deleted.")
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
