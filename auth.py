import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'Student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Seed default accounts if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_users = [
            ("Alok Gupta", "alok@placement.edu", "alok123", "Placement Officer"),
            ("Demo Student", "demo@placement.edu", "demo123", "Student Candidate")
        ]
        for name, email, password, role in seed_users:
            p_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (name, email.lower(), p_hash, role))
        conn.commit()
    conn.close()

def register_user(name, email, password, role="Student"):
    name = name.strip()
    email = email.strip().lower()
    password = password.strip()
    
    if not name or not email or not password:
        return False, "All fields are required.", None
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters.", None

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        p_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, p_hash, role))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        user = dict(row)
        conn.close()
        return True, "Account registered successfully!", user
    except sqlite3.IntegrityError:
        conn.close()
        return False, "An account with this email already exists.", None
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}", None

def authenticate_user(email, password):
    email = email.strip().lower()
    password = password.strip()

    if not email or not password:
        return False, "Email and password are required.", None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash, role, created_at FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "Invalid email or password.", None

    if not check_password_hash(row["password_hash"], password):
        return False, "Invalid email or password.", None

    user = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
        "created_at": row["created_at"]
    }
    return True, "Login successful!", user

def get_user_by_id(user_id):
    if not user_id:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Initialize on import
init_db()
