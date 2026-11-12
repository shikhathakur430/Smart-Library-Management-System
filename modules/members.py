import pandas as pd
from database import get_connection

def get_members(search=""):
    with get_connection() as conn:
        if search:
            term = f"%{search}%"
            rows = conn.execute("""SELECT * FROM members
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? ORDER BY name""",
                (term, term, term)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    return pd.DataFrame([dict(r) for r in rows])

def add_member(name, email, phone):
    with get_connection() as conn:
        conn.execute("INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
                     (name.strip(), email.strip().lower(), phone.strip()))
        conn.commit()

def delete_member(member_id):
    with get_connection() as conn:
        active = conn.execute("SELECT COUNT(*) FROM borrowings WHERE member_id=? AND status='Borrowed'", (member_id,)).fetchone()[0]
        if active:
            raise ValueError("This member has a book that has not been returned.")
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
        conn.commit()
