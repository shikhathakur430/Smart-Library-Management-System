# Smart Library Management System

A student-friendly library management web application built with Python, Streamlit, SQLite, Pandas and Plotly.

## Features
- Dashboard with inventory and borrowing metrics
- Add, update, delete and search books
- Register, search and remove members
- Issue and return books with due dates
- Borrowing history and popular-book statistics
- Category-based recommendations using a member's borrowing history
- Persistent SQLite database

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows (PowerShell)

```powershell
cd Smart_Library_Management
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks virtual-environment activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Then open the local URL printed in the terminal (usually http://localhost:8501).

## Database
The SQLite database is created automatically at `data/library.db` the first time the app runs. Sample books are inserted automatically when the database is empty.

## Project structure

```text
Smart_Library_Management/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── data/
└── modules/
    ├── books.py
    ├── members.py
    ├── borrowing.py
    ├── analytics.py
    └── recommendations.py
```

## Notes
- Book/member IDs are generated automatically.
- A book cannot be issued when no copies are available.
- A book or member with an active borrowing cannot be deleted.
- Reducing total copies below the number currently on loan is blocked.
- This is an educational project, not a production-ready library platform. Add authentication, backups, audit logging and deployment hardening before real institutional use.
