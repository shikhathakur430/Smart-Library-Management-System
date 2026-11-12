import pandas as pd
from database import get_connection

def dashboard_metrics():
    with get_connection() as conn:
        books = conn.execute("SELECT COALESCE(SUM(total_copies),0) FROM books").fetchone()[0]
        available = conn.execute("SELECT COALESCE(SUM(available_copies),0) FROM books").fetchone()[0]
        members = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM borrowings WHERE status='Borrowed'").fetchone()[0]
        returned = conn.execute("SELECT COUNT(*) FROM borrowings WHERE status='Returned'").fetchone()[0]
    return {"total_copies": books, "available": available, "members": members,
            "borrowed": active, "returned": returned}

def category_stats():
    with get_connection() as conn:
        rows = conn.execute("SELECT category, SUM(total_copies) AS copies FROM books GROUP BY category ORDER BY copies DESC").fetchall()
    return pd.DataFrame([dict(r) for r in rows])

def popular_books():
    with get_connection() as conn:
        rows = conn.execute("""SELECT b.title, COUNT(br.id) AS borrow_count
            FROM books b LEFT JOIN borrowings br ON b.id=br.book_id
            GROUP BY b.id ORDER BY borrow_count DESC, b.title LIMIT 10""").fetchall()
    return pd.DataFrame([dict(r) for r in rows])
