# View database contents
import os
import sqlite3
import sys

print("Starting database view script...")
sys.stdout.flush()

# Path to database
DB_PATH = os.path.join('instance', 'users.db')
print(f"Looking for database at: {os.path.abspath(DB_PATH)}")
sys.stdout.flush()

# Check if database exists
if not os.path.exists(DB_PATH):
    print(f"Database file not found at: {DB_PATH}")
    exit(1)

# Connect to database
try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query all users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
      # Print table header
    header = "\n{:<5} {:<15} {:<25} {:<15} {:<20}".format(
        "ID", "Username", "Email", "Password", "Created At"
    )
    print(header)
    sys.stdout.flush()
    
    print("-" * 80)
    sys.stdout.flush()
    
    # Print each user (omitting full password hash for security)
    for user in users:
        user_info = "{:<5} {:<15} {:<25} {:<15} {:<20}".format(
            user['id'],
            user['username'],
            user['email'],
            user['password'][:10] + "...",
            user['created_at']
        )
        print(user_info)
        sys.stdout.flush()
    
    # Print total count
    print("-" * 80)
    print(f"Total users: {len(users)}")
    
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if conn:
        conn.close()
