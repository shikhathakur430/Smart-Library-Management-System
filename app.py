import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, get_connection
from modules.books import get_books, add_book, update_book, delete_book
from modules.members import get_members, add_member, delete_member
from modules.borrowing import issue_book, return_book, get_borrowings
from modules.analytics import dashboard_metrics, category_stats, popular_books
from modules.recommendations import recommend_books

st.set_page_config(page_title="Smart Library Management", page_icon="📚", layout="wide")
init_db()

st.markdown("""
<style>
    .stApp {background: #f5f7fb;}
    [data-testid="stSidebar"] {background: #172554;}
    [data-testid="stSidebar"] * {color: white !important;}
    .main-title {font-size: 2.1rem; font-weight: 800; color: #172554; margin-bottom: 0;}
    .sub-title {color: #64748b; margin-top: 0.2rem;}
    div[data-testid="stMetric"] {background: white; padding: 18px; border-radius: 12px; border: 1px solid #e5e7eb;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📚 Smart Library")
st.sidebar.caption("Library administration portal")
page = st.sidebar.radio("Navigation", ["Dashboard", "Books", "Members", "Issue / Return", "Recommendations", "About"])
st.sidebar.divider()
st.sidebar.caption("Student Project • Python + Streamlit + SQLite")

def show_table(df):
    if df.empty:
        st.info("No records found yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def safe_action(fn, success):
    try:
        fn()
        st.success(success)
        st.rerun()
    except Exception as e:
        st.error(str(e))

if page == "Dashboard":
    st.markdown('<p class="main-title">Library Dashboard</p><p class="sub-title">A quick overview of your library activity.</p>', unsafe_allow_html=True)
    m = dashboard_metrics()
    cols = st.columns(4)
    cols[0].metric("Book copies", m["total_copies"])
    cols[1].metric("Available copies", m["available"])
    cols[2].metric("Registered members", m["members"])
    cols[3].metric("Currently borrowed", m["borrowed"])
    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Books by category")
        cat = category_stats()
        if not cat.empty:
            fig = px.pie(cat, names="category", values="copies", hole=0.48)
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add books to see category statistics.")
    with right:
        st.subheader("Most borrowed books")
        popular = popular_books()
        if not popular.empty:
            fig = px.bar(popular, x="borrow_count", y="title", orientation="h",
                         labels={"borrow_count":"Times borrowed","title":"Book"})
            fig.update_layout(yaxis={"categoryorder":"total ascending"}, margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("Recent borrowing activity")
    show_table(get_borrowings().head(8))

elif page == "Books":
    st.markdown('<p class="main-title">Book Catalogue</p><p class="sub-title">Add, find, update and remove books.</p>', unsafe_allow_html=True)
    search = st.text_input("🔎 Search by title, author, category or ISBN")
    show_table(get_books(search))
    st.divider()
    add_tab, edit_tab, delete_tab = st.tabs(["➕ Add book", "✏️ Update book", "🗑️ Delete book"])
    with add_tab:
        with st.form("add_book_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            title = c1.text_input("Book title *")
            author = c2.text_input("Author *")
            category = c1.selectbox("Category", ["Programming","Science","Fiction","Self-help","Biography","History","Mathematics","Other"])
            isbn = c2.text_input("ISBN (optional)")
            copies = st.number_input("Number of copies", min_value=1, max_value=500, value=1)
            submitted = st.form_submit_button("Add book", type="primary")
            if submitted:
                if not title.strip() or not author.strip():
                    st.error("Title and author are required.")
                else:
                    safe_action(lambda: add_book(title, author, category, isbn, int(copies)), "Book added successfully.")
    with edit_tab:
        df = get_books()
        if not df.empty:
            selected = st.selectbox("Select book", df["id"].tolist(), format_func=lambda x: f'{x} — {df.loc[df.id==x, "title"].iloc[0]}')
            row = df[df.id == selected].iloc[0]
            with st.form("edit_book_form"):
                et = st.text_input("Title", str(row.title))
                ea = st.text_input("Author", str(row.author))
                ec = st.text_input("Category", str(row.category))
                ei = st.text_input("ISBN", "" if pd.isna(row.isbn) else str(row.isbn))
                copies = st.number_input("Total copies", min_value=1, max_value=500, value=int(row.total_copies))
                if st.form_submit_button("Save changes"):
                    safe_action(lambda: update_book(int(selected), et, ea, ec, ei, int(copies)), "Book updated.")
        else:
            st.info("Add a book first.")
    with delete_tab:
        df = get_books()
        if not df.empty:
            selected = st.selectbox("Book to delete", df["id"].tolist(), format_func=lambda x: f'{x} — {df.loc[df.id==x, "title"].iloc[0]}', key="delete_book")
            if st.button("Delete selected book", type="secondary"):
                safe_action(lambda: delete_book(int(selected)), "Book deleted.")
        else:
            st.info("No books to delete.")

elif page == "Members":
    st.markdown('<p class="main-title">Library Members</p><p class="sub-title">Manage member registrations and details.</p>', unsafe_allow_html=True)
    search = st.text_input("Search members by name, email or phone")
    show_table(get_members(search))
    st.divider()
    add_tab, delete_tab = st.tabs(["➕ Register member", "🗑️ Remove member"])
    with add_tab:
        with st.form("add_member_form", clear_on_submit=True):
            name = st.text_input("Full name *")
            email = st.text_input("Email address *")
            phone = st.text_input("Phone number")
            if st.form_submit_button("Register member", type="primary"):
                if not name.strip() or not email.strip() or "@" not in email:
                    st.error("Enter a name and a valid email address.")
                else:
                    safe_action(lambda: add_member(name, email, phone), "Member registered successfully.")
    with delete_tab:
        df = get_members()
        if not df.empty:
            selected = st.selectbox("Member to remove", df["id"].tolist(), format_func=lambda x: f'{x} — {df.loc[df.id==x, "name"].iloc[0]}')
            if st.button("Remove selected member"):
                safe_action(lambda: delete_member(int(selected)), "Member removed.")
        else:
            st.info("No members registered.")

elif page == "Issue / Return":
    st.markdown('<p class="main-title">Borrowing Desk</p><p class="sub-title">Issue books and record returns.</p>', unsafe_allow_html=True)
    issue_tab, return_tab, history_tab = st.tabs(["📤 Issue a book", "📥 Return a book", "📋 Borrowing history"])
    with issue_tab:
        with get_connection() as conn:
            books = conn.execute("SELECT id,title,available_copies FROM books WHERE available_copies>0 ORDER BY title").fetchall()
            members = conn.execute("SELECT id,name,email FROM members ORDER BY name").fetchall()
        if books and members:
            with st.form("issue_form"):
                book_id = st.selectbox("Available book", [r["id"] for r in books], format_func=lambda x: next(f'{r["title"]} ({r["available_copies"]} available)' for r in books if r["id"]==x))
                member_id = st.selectbox("Member", [r["id"] for r in members], format_func=lambda x: next(f'{r["name"]} — {r["email"]}' for r in members if r["id"]==x))
                days = st.number_input("Loan period (days)", min_value=1, max_value=90, value=14)
                if st.form_submit_button("Issue book", type="primary"):
                    safe_action(lambda: issue_book(int(book_id), int(member_id), int(days)), "Book issued successfully.")
        else:
            st.info("You need at least one available book and one registered member before issuing.")
    with return_tab:
        active = get_borrowings(active_only=True)
        if not active.empty:
            selected = st.selectbox("Active borrowing", active["id"].tolist(),
                format_func=lambda x: f'#{x} — {active.loc[active.id==x, "book"].iloc[0]} / {active.loc[active.id==x, "member"].iloc[0]}')
            if st.button("Confirm return", type="primary"):
                safe_action(lambda: return_book(int(selected)), "Book return recorded.")
        else:
            st.success("There are no books currently on loan.")
    with history_tab:
        show_table(get_borrowings())

elif page == "Recommendations":
    st.markdown('<p class="main-title">Smart Recommendations</p><p class="sub-title">Suggestions based on borrowing preferences and available stock.</p>', unsafe_allow_html=True)
    members = get_members()
    member_id = None
    if not members.empty:
        option = st.selectbox("Choose a member (optional)", ["General recommendations"] + members["id"].tolist(),
            format_func=lambda x: "General recommendations" if x == "General recommendations" else members.loc[members.id==x, "name"].iloc[0])
        if option != "General recommendations":
            member_id = int(option)
    recommendations, reason = recommend_books(member_id)
    st.caption(reason)
    if recommendations:
        cols = st.columns(min(3, len(recommendations)))
        for i, book in enumerate(recommendations):
            with cols[i % len(cols)]:
                st.markdown(f"**{book['title']}**")
                st.write(f"By {book['author']}")
                st.caption(f"{book['category']} • {book['available_copies']} available")
                st.divider()
    else:
        st.info("No available recommendations. Add more books or check current stock.")

elif page == "About":
    st.markdown('<p class="main-title">About this project</p>', unsafe_allow_html=True)
    st.write("The Smart Library Management System is a student-level database application built with Python, Streamlit and SQLite.")
    st.subheader("Core modules")
    st.markdown("""
    - **Catalogue management:** maintain book details and stock.
    - **Member management:** register and search members.
    - **Circulation:** issue and return books with due dates.
    - **Analytics:** monitor inventory, categories and popular titles.
    - **Recommendations:** suggest available books using a member's borrowing categories.
    """)
    st.info("This is a demonstration project. It does not include authentication, fines, barcode scanning or cloud hosting.")
    st.caption("Built with Python • Streamlit • SQLite • Pandas • Plotly")
