# database.py

import sqlite3
from datetime import datetime
import hashlib

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect('app.db')  # Use a single database file
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # Create quiz_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_admin_user():
    """Add an admin user to the database if one doesn't already exist."""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    result = cursor.fetchone()
    if not result:
        # Hash the password
        password = 'admin123'  # Default password for admin
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_password))
    conn.commit()
    conn.close()

def add_sample_users():
    """Add sample users to the database."""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    sample_users = [
        ('john_doe', 'password1'),
        ('jane_smith', 'password2'),
        ('alice_wonder', 'password3'),
    ]
    for username, password in sample_users:
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        except sqlite3.IntegrityError:
            pass  # User already exists
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """Authenticate the user with the provided credentials."""
    password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_quiz_result(username, score):
    """Save the quiz result to the database."""
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO quiz_results (username, score, timestamp) VALUES (?, ?, ?)",
        (username, score, timestamp)
    )
    conn.commit()
    conn.close()

def get_all_quiz_results():
    """Retrieve all quiz results from the database."""
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, score, timestamp FROM quiz_results")
    results = cursor.fetchall()
    conn.close()
    return results

# Initialize the database
init_db()
add_admin_user()
add_sample_users()
