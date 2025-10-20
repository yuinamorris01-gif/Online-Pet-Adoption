#!/usr/bin/env python3
"""
Direct login test to simulate the exact login process
"""
import sqlite3
from werkzeug.security import check_password_hash

def test_login_process():
    print("=== DIRECT LOGIN TEST ===\n")
    
    # Simulate the exact login process from the app
    username = "admin"
    password = "admin123"
    
    print(f"Testing login with:")
    print(f"  Username: '{username}'")
    print(f"  Password: '{password}'")
    print(f"  Username length: {len(username)} chars")
    print(f"  Password length: {len(password)} chars")
    
    # Check validation rules (from our improved login)
    print(f"\n=== VALIDATION CHECKS ===")
    
    # Basic validation
    if not username:
        print("❌ Username is empty")
        return False
    else:
        print("✅ Username is not empty")
        
    if not password:
        print("❌ Password is empty") 
        return False
    else:
        print("✅ Password is not empty")
    
    if len(username) < 3:
        print("❌ Username too short (< 3 chars)")
        return False
    else:
        print("✅ Username length OK")
        
    if len(password) < 6:
        print("❌ Password too short (< 6 chars)")
        return False
    else:
        print("✅ Password length OK")
    
    # Database lookup
    print(f"\n=== DATABASE LOOKUP ===")
    try:
        conn = sqlite3.connect('pet_adoption.db')
        conn.row_factory = sqlite3.Row
        
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username, username)
        ).fetchone()
        
        if user:
            print(f"✅ User found: {user['username']}")
            print(f"  - Email: {user['email']}")
            print(f"  - Role: {user['role']}")
            
            # Password verification
            if check_password_hash(user['password_hash'], password):
                print("✅ Password verification: SUCCESS")
                print(f"\n🎉 LOGIN SHOULD WORK!")
                print(f"Session would be set with:")
                print(f"  - user_id: {user['id']}")
                print(f"  - username: {user['username']}")
                print(f"  - role: {user['role']}")
                return True
            else:
                print("❌ Password verification: FAILED")
                return False
        else:
            print("❌ User not found in database")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = test_login_process()
    
    if success:
        print(f"\n✅ LOGIN TEST: PASSED")
        print(f"\nIf you're still having issues:")
        print(f"1. Clear your browser cache/cookies")
        print(f"2. Try in incognito/private mode")
        print(f"3. Check browser console for JavaScript errors")
        print(f"4. Make sure you're typing exactly: admin / admin123")
    else:
        print(f"\n❌ LOGIN TEST: FAILED")
        print(f"There's an issue with the login logic.")
