import sqlite3
from pathlib import Path


# =========================
# Database Path
# =========================
DB_PATH = Path(__file__).parent / "access.db"


# =========================
# Initialize Database
# =========================
def init_db():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # =========================
    # Users
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )
    """)

    # =========================
    # Logs
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT NOT NULL,
        name TEXT,
        ai_result TEXT NOT NULL,
        admin_result TEXT DEFAULT 'PENDING',
        time TIMESTAMP NOT NULL,
        image_path TEXT,
        similarity REAL DEFAULT 0.0,
        attempt_count INTEGER DEFAULT 1
    )
    """)

    # =========================
    # Face Embeddings
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS face_embeddings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        embedding BLOB NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # =========================
    # Default User
    # =========================
    cur.execute("""
    INSERT OR IGNORE INTO users(uid, name, active)
    VALUES('BC6EF306', 'Cuong', 1)
    """)

    # =========================
    # Commit
    # =========================
    conn.commit()
    conn.close()

    print("Database initialized successfully.")


# =========================
# Run Directly
# =========================
if __name__ == "__main__":
    init_db()
