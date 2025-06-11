# Seed database with initial users for demonstrating SQL injection
import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys

# Print absolute path for debugging
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Path to database
DB_PATH = os.path.join('instance', 'users.db')
print(f"Database path: {os.path.abspath(DB_PATH)}")

# Ensure the instance directory exists
os.makedirs('instance', exist_ok=True)

# Connect to database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_login TEXT
    )
''')

# Clear existing data
cursor.execute('DELETE FROM users')

# Sample users
users = [
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123456',
        'created_at': '2025-01-01 00:00:00'
    },
    {
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'password123',
        'created_at': '2025-01-02 10:30:00'
    },
    {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'secret12345',
        'created_at': '2025-01-03 15:45:00'
    },
    {
        'username': 'jane_smith',
        'email': 'jane@example.com',
        'password': 'mysecret1234',
        'created_at': '2025-01-04 08:20:00'
    },
    {
        'username': 'security_expert',
        'email': 'expert@secure.org',
        'password': 'ComplexP@ssw0rd!',
        'created_at': '2025-01-05 12:10:00'
    }
]

# Insert users
for user in users:
    try:
        hashed_password = generate_password_hash(user['password'])
        cursor.execute(
            'INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)',
            (user['username'], user['email'], hashed_password, user['created_at'])
        )
        print(f"Added user: {user['username']}")
    except sqlite3.IntegrityError as e:
        print(f"Error adding {user['username']}: {e}")

# Commit changes and close connection
conn.commit()
conn.close()

print("\nDatabase has been seeded with test users!")
print("Try logging in with:")
print("Username: 'admin', Password: 'admin123456'")
print("Or try SQL injection with username: ' OR '1'='1")
