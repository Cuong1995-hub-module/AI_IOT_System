from pathlib import Path
import sqlite3
from unicodedata import name

DB_PATH = Path(__file__).parent / "access.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_uid(uid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, uid, name, active
        FROM users
        WHERE uid = ?
        """,
        (uid,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def add_user(uid, name, active=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users(uid, name, active)
        VALUES (?, ?, ?)
        """,
        (uid, name, active)
    )

    conn.commit()
    conn.close()


def delete_user(uid):

    user = check_uid(uid)

    if user is None:
        return False

    # Delete face embedding first
    delete_embeddings(user["id"])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE uid = ?
    """, (uid,))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted > 0

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
    users.id,
    users.uid,
    users.name,
    users.active,

    CASE
        WHEN face_embeddings.user_id IS NULL THEN 0
        ELSE 1
    END AS has_face

FROM users

LEFT JOIN face_embeddings
ON users.id = face_embeddings.user_id

ORDER BY users.id
        """
    )

    users = cursor.fetchall()

    conn.close()

    return users

from datetime import datetime

def save_log(uid, name, result, image_path=None, similarity=0.0):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()

    MAX_ATTEMPTS = 3


    # =========================
    # Check today's existing log
    # =========================

    cursor.execute("""
        SELECT
            id,
            admin_result,
            attempt_count
        FROM logs
        WHERE uid = ?
        AND DATE(time) = DATE(?)
        ORDER BY time DESC
        LIMIT 1
    """, (
        uid,
        now
    ))

    existing = cursor.fetchone()

    # =========================
    # Already checked today
    # =========================

    if existing:

        log_id = existing[0]
        current_admin = existing[1]
        current_attempts = existing[2] or 1

        # Already approved → LOCK
        if current_admin == "APPROVED":

            conn.close()

            return {
                "status": "LOCKED",
                "log_id": log_id,
                "attempt_count": current_attempts
            }

        # Maximum attempts reached → LOCK
        if current_attempts >= MAX_ATTEMPTS:

            conn.close()

            return {
                "status": "MAX_ATTEMPTS",
                "log_id": log_id,
                "attempt_count": current_attempts
            }

        # =========================
        # Re-check
        # =========================

        new_attempts = current_attempts + 1

    else:

        # First attempt today
        new_attempts = 1

    # =========================
    # AI threshold by attempt
    # =========================

    if new_attempts == 1:
        auto_approve_threshold = 0.70

    elif new_attempts == 2:
        auto_approve_threshold = 0.65

    else:
        auto_approve_threshold = 0.60

    # =========================
    # Calculate Admin Decision
    # =========================

    if name == "Unknown":

        admin_result = "REJECTED"

    elif result == "MATCH" and similarity >= auto_approve_threshold:

        admin_result = "APPROVED"

    else:

        admin_result = "PENDING"

    # =========================
    # UPDATE existing log
    # =========================

    if existing:

        cursor.execute("""
            UPDATE logs
            SET
                name = ?,
                ai_result = ?,
                admin_result = ?,
                time = ?,
                image_path = ?,
                similarity = ?,
                attempt_count = ?
            WHERE id = ?
        """, (
            name,
            result,
            admin_result,
            now,
            image_path,
            similarity,
            new_attempts,
            log_id
        ))

        conn.commit()
        conn.close()

        return {
            "status": admin_result,
            "log_id": log_id,
            "attempt_count": new_attempts,
            "similarity": similarity
        }

    # =========================
    # CREATE first log
    # =========================

    cursor.execute("""
        INSERT INTO logs (
            uid,
            name,
            ai_result,
            admin_result,
            time,
            image_path,
            similarity,
            attempt_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        name,
        result,
        admin_result,
        now,
        image_path,
        similarity,
        new_attempts
    ))

    log_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": admin_result,
        "log_id": log_id,
        "attempt_count": new_attempts,
        "similarity": similarity
    }


def get_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            uid,
            name,
            ai_result,
            admin_result,
            time,
            image_path,
            similarity,
            attempt_count
        FROM logs
        ORDER BY time DESC
        LIMIT ?
        """,
        (limit,)
    )

    logs = cursor.fetchall()

    conn.close()

    return logs

def get_logs_by_date(date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            uid,
            name,
            ai_result,
            admin_result,
            time,
            image_path,
            similarity,
            attempt_count
        FROM logs
        WHERE DATE(time) = ?
        ORDER BY time DESC
    """, (date,))

    logs = cursor.fetchall()

    conn.close()

    return logs

def export_logs_by_date(date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
    uid,
    name,
    ai_result,
    admin_result,
    time
FROM logs
        WHERE DATE(time) = ?
        ORDER BY time DESC
    """, (date,))

    logs = cursor.fetchall()

    conn.close()

    return logs

def get_verified_today():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE admin_result='APPROVED'
        AND DATE(time)=DATE('now','localtime')
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count

def get_denied_today():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE admin_result='REJECTED'
        AND DATE(time)=DATE('now','localtime')
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


def update_user(uid, name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET name = ?
        WHERE uid = ?
    """, (name, uid))

    updated = cursor.rowcount

    conn.commit()
    conn.close()

    return updated > 0
def save_embedding(user_id, embedding):

    conn = get_connection()
    cursor = conn.cursor()

    embedding_blob = embedding.astype(
        "float32"
    ).tobytes()

    cursor.execute("""
        DELETE FROM face_embeddings
        WHERE user_id = ?
    """, (user_id,))

    cursor.execute("""
        INSERT INTO face_embeddings(
            user_id,
            embedding
        )
        VALUES (?, ?)
    """, (
        user_id,
        embedding_blob
    ))

    conn.commit()
    conn.close()

    return True

def get_embeddings():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            face_embeddings.user_id,
            users.uid,
            users.name,
            face_embeddings.embedding
        FROM face_embeddings
        JOIN users
        ON users.id = face_embeddings.user_id
    """)

    embeddings = cursor.fetchall()

    conn.close()

    return embeddings

def get_embedding_by_uid(uid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.uid,
            users.name,
            face_embeddings.embedding
        FROM face_embeddings
        JOIN users
        ON users.id = face_embeddings.user_id
        WHERE users.uid = ?
    """, (uid,))

    embedding = cursor.fetchone()

    conn.close()

    return embedding

def delete_embeddings(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM face_embeddings
        WHERE user_id = ?
    """, (user_id,))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted > 0

# =========================
# Admin Decision
# =========================

def approve_log(log_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE logs
        SET admin_result = 'APPROVED'
        WHERE id = ?
    """, (log_id,))

    conn.commit()
    conn.close()

    return True


def reject_log(log_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE logs
        SET admin_result = 'REJECTED'
        WHERE id = ?
    """, (log_id,))

    conn.commit()
    conn.close()

    return True

def get_today_log(uid):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            uid,
            name,
            ai_result,
            admin_result,
            time,
            image_path,
            similarity,
            attempt_count
        FROM logs
        WHERE uid = ?
        AND DATE(time) = DATE('now', 'localtime')
        ORDER BY time DESC
        LIMIT 1
    """, (uid,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None