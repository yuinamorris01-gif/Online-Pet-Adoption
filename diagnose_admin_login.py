import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def diagnose_admin_login():
    print("=== ADMIN LOGIN DIAGNOSTIC ===\n")
    
    try:
        conn = sqlite3.connect('pet_adoption.db')
        conn.row_factory = sqlite3.Row
        
        # Get admin user details
        admin_user = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        
        if not admin_user:
            print("❌ CRITICAL: Admin user not found!")
            return
        
        print(f"✓ Admin user found:")
        print(f"  - ID: {admin_user['id']}")
        print(f"  - Username: {admin_user['username']}")
        print(f"  - Email: {admin_user['email']}")
        print(f"  - Role: {admin_user['role']}")
        print(f"  - Full Name: {admin_user['full_name']}")
        print(f"  - Password Hash: {admin_user['password_hash'][:50]}...")
        
        # Test password verification
        test_password = "admin123"
        print(f"\n=== PASSWORD VERIFICATION TEST ===")
        print(f"Testing password: '{test_password}'")
        
        is_valid = check_password_hash(admin_user['password_hash'], test_password)
        
        if is_valid:
            print("✅ Password verification: SUCCESS")
        else:
            print("❌ Password verification: FAILED")
            
            # Try to regenerate the password hash
            print(f"\n=== REGENERATING ADMIN PASSWORD ===")
            new_hash = generate_password_hash(test_password)
            
            # Update the admin user with new hash
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE username = 'admin'",
                (new_hash,)
            )
            conn.commit()
            
            # Test again
            admin_user = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
            is_valid_new = check_password_hash(admin_user['password_hash'], test_password)
            
            if is_valid_new:
                print("✅ Password regenerated and verified successfully!")
            else:
                print("❌ Still failed after regeneration - there may be a deeper issue")
        
        # Test with different variations
        print(f"\n=== TESTING PASSWORD VARIATIONS ===")
        test_passwords = ["admin123", "Admin123", "ADMIN123", "admin", "123"]
        
        for test_pwd in test_passwords:
            is_match = check_password_hash(admin_user['password_hash'], test_pwd)
            status = "✅" if is_match else "❌"
            print(f"{status} Testing '{test_pwd}': {'MATCH' if is_match else 'NO MATCH'}")
        
        # Check if there are any other admin users
        print(f"\n=== CHECKING FOR OTHER ADMIN USERS ===")
        all_admins = conn.execute("SELECT username, email FROM users WHERE role = 'admin'").fetchall()
        print(f"Total admin users found: {len(all_admins)}")
        for admin in all_admins:
            print(f"  - {admin['username']} ({admin['email']})")
        
        conn.close()
        
        print(f"\n=== RECOMMENDATIONS ===")
        print("1. Try logging in with:")
        print("   Username: admin")
        print("   Password: admin123")
        print("2. Make sure you're using the exact credentials above")
        print("3. Check for any typos or extra spaces")
        print("4. If still failing, the password has been regenerated - try again")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")

if __name__ == "__main__":
    diagnose_admin_login()
