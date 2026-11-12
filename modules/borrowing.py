import pandas as pd
from datetime import date, timedelta
from database import get_connection

def issue_book(book_id, member_id, days=14):
    with get_connection() as conn:
        book = conn.execute("SELECT available_copies FROM books WHERE id=?", (book_id,)).fetchone()
        if not book or book["available_copies"] < 1:
            raise ValueError("No copies of this book are currently available.")
        conn.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?", (book_id,))
        due = (date.today() + timedelta(days=days)).isoformat()
        conn.execute("""INSERT INTO borrowings (book_id, member_id, due_date)
            VALUES (?, ?, ?)""", (book_id, member_id, due))
        conn.commit()

def return_book(borrowing_id):
    with get_connection() as conn:
        row = conn.execute("SELECT book_id, status FROM borrowings WHERE id=?", (borrowing_id,)).fetchone()
        if not row or row["status"] != "Borrowed":
            raise ValueError("This borrowing is not active.")
        conn.execute("""UPDATE borrowings SET status='Returned', return_date=?
            WHERE id=?""", (date.today().isoformat(), borrowing_id))
        conn.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?", (row["book_id"],))
        conn.commit()

def get_borrowings(active_only=False):
    query = """SELECT br.id, b.title AS book, m.name AS member, br.issue_date,
        br.due_date, br.return_date, br.status
        FROM borrowings br JOIN books b ON br.book_id=b.id
        JOIN members m ON br.member_id=m.id"""
    if active_only:
        query += " WHERE br.status='Borrowed'"
    query += " ORDER BY br.issue_date DESC, br.id DESC"
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return pd.DataFrame([dict(r) for r in rows])
