import sqlite3

try:
    conn = sqlite3.connect('pet_adoption.db')
    
    print("=== DATABASE STRUCTURE CHECK ===")
    
    # Check tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Tables: {[row[0] for row in tables]}")
    
    # Check admin user
    admin_user = conn.execute("SELECT username, email FROM users WHERE role='admin'").fetchone()
    print(f"Admin user exists: {admin_user}")
    
    # Count total users
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"Total users: {user_count}")
    
    conn.close()
    print("✓ Database structure looks good!")
    
except Exception as e:
    print(f"✗ Database error: {e}")
