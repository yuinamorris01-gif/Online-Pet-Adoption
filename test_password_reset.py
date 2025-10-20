#!/usr/bin/env python3
"""
Test script to validate password reset functionality
"""
import sqlite3
from datetime import datetime, timedelta
import uuid

def test_password_reset_workflow():
    """Test the password reset token generation and validation"""
    print("=== TESTING PASSWORD RESET FUNCTIONALITY ===\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect('pet_adoption.db')
        conn.row_factory = sqlite3.Row
        
        # Check if admin user exists
        admin_user = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        
        if not admin_user:
            print("✗ Admin user not found")
            return False
        
        print(f"✓ Found admin user: {admin_user['email']}")
        
        # Generate a test password reset token
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Insert test token
        conn.execute(
            'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
            (admin_user['id'], token, expires_at)
        )
        conn.commit()
        print(f"✓ Generated test reset token: {token[:8]}...")
        
        # Verify token exists and is valid
        reset_record = conn.execute(
            'SELECT user_id, expires_at FROM password_reset_tokens WHERE token = ?',
            (token,)
        ).fetchone()
        
        if reset_record:
            token_expires = datetime.fromisoformat(reset_record['expires_at'])
            if token_expires > datetime.now():
                print("✓ Token is valid and not expired")
            else:
                print("✗ Token is expired")
                return False
        else:
            print("✗ Token not found in database")
            return False
        
        # Clean up test token
        conn.execute('DELETE FROM password_reset_tokens WHERE token = ?', (token,))
        conn.commit()
        print("✓ Test token cleaned up")
        
        # Check password reset tokens table structure
        columns = conn.execute("PRAGMA table_info(password_reset_tokens)").fetchall()
        expected_columns = {'user_id', 'token', 'expires_at', 'created_at'}
        actual_columns = {col[1] for col in columns}
        
        if expected_columns.issubset(actual_columns):
            print("✓ Password reset tokens table has correct structure")
        else:
            missing = expected_columns - actual_columns
            print(f"✗ Missing columns in password_reset_tokens table: {missing}")
            return False
        
        conn.close()
        
        print("\n=== PASSWORD RESET TEST RESULTS ===")
        print("✓ All password reset functionality tests passed!")
        print("\nPassword reset features:")
        print("• Token generation and storage")
        print("• Token expiration validation")
        print("• Database schema integrity")
        print("\nTo test the full workflow:")
        print("1. Run: python app.py")
        print("2. Go to: http://127.0.0.1:5000/login")
        print("3. Click 'Forgot Password?'")
        print("4. Enter: admin@petadoption.com")
        print("5. Check the flash message for the reset link")
        print("6. Follow the reset link to change password")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing password reset functionality: {e}")
        return False

if __name__ == "__main__":
    test_password_reset_workflow()
