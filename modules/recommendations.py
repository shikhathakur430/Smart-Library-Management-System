from database import get_connection

def recommend_books(member_id=None, limit=5):
    with get_connection() as conn:
        if member_id:
            categories = conn.execute("""SELECT b.category, COUNT(*) AS n
                FROM borrowings br JOIN books b ON br.book_id=b.id
                WHERE br.member_id=? GROUP BY b.category ORDER BY n DESC LIMIT 2""",
                (member_id,)).fetchall()
            preferred = [r["category"] for r in categories]
            if preferred:
                marks = ",".join("?" for _ in preferred)
                rows = conn.execute(f"""SELECT * FROM books WHERE available_copies>0
                    AND category IN ({marks}) ORDER BY title LIMIT ?""",
                    (*preferred, limit)).fetchall()
                if rows:
                    return [dict(r) for r in rows], "Based on this member's borrowing history"
        rows = conn.execute("""SELECT * FROM books WHERE available_copies>0
            ORDER BY category, title LIMIT ?""", (limit,)).fetchall()
    return [dict(r) for r in rows], "Popular categories and currently available books"
