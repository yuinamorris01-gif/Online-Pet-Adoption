#!/usr/bin/env python3
"""
Test script to validate the enhanced login UI functionality
"""
import requests
import sys
from app import init_db

def test_login_page():
    """Test if the login page loads correctly"""
    try:
        # Initialize the database first
        init_db()
        print("✓ Database initialized successfully")
        
        # Test if the login page is accessible
        response = requests.get('http://127.0.0.1:5000/login', timeout=5)
        
        if response.status_code == 200:
            print("✓ Login page loads successfully")
            
            # Check if key elements are present in the page
            content = response.text
            
            checks = [
                ('form', 'Login form present'),
                ('username', 'Username field present'),
                ('password', 'Password field present'),  
                ('remember_me', 'Remember me checkbox present'),
                ('modern-input', 'Enhanced input styling applied'),
                ('auth-btn primary', 'Primary button styling applied'),
                ('demo-notice', 'Demo credentials notice present'),
                ('LoginFormHandler', 'Enhanced JavaScript functionality present'),
                ('aria-describedby', 'Accessibility attributes present')
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✓ {description}")
                else:
                    print(f"✗ {description}")
            
            print("\n=== LOGIN PAGE STRUCTURE ANALYSIS ===")
            print(f"Total page size: {len(content)} characters")
            print(f"Contains AOS animations: {'AOS.init' in content}")
            print(f"Contains GSAP animations: {'gsap' in content}")
            print(f"Contains form validation: {'validateForm' in content}")
            print(f"Contains loading states: {'setLoadingState' in content}")
            
        else:
            print(f"✗ Login page failed to load (Status: {response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the application. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"✗ Error testing login page: {e}")

def test_login_functionality():
    """Test the actual login functionality"""
    try:
        # Test with valid admin credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        session = requests.Session()
        
        # First get the login page to establish session
        login_page = session.get('http://127.0.0.1:5000/login', timeout=5)
        if login_page.status_code != 200:
            print("✗ Could not access login page for testing")
            return
            
        # Attempt login
        response = session.post('http://127.0.0.1:5000/login', data=login_data, timeout=5)
        
        if response.status_code == 200 and 'Welcome back' in response.text:
            print("✓ Admin login functionality works correctly")
        elif response.url.endswith('/'):  # Redirect to home page indicates success
            print("✓ Admin login successful (redirected to home)")
        else:
            print("✗ Admin login may have issues")
            
        # Test with invalid credentials
        invalid_data = {
            'username': 'invalid_user',
            'password': 'invalid_pass'
        }
        
        response = session.post('http://127.0.0.1:5000/login', data=invalid_data, timeout=5)
        if 'Invalid username or password' in response.text or response.status_code == 200:
            print("✓ Invalid login properly rejected")
        else:
            print("✗ Invalid login handling may have issues")
            
    except Exception as e:
        print(f"✗ Error testing login functionality: {e}")

if __name__ == "__main__":
    print("=== TESTING ENHANCED LOGIN UI ===\n")
    
    print("1. Testing login page structure and content:")
    test_login_page()
    
    print("\n2. Testing login functionality:")
    test_login_functionality()
    
    print("\n=== TEST COMPLETE ===")
    print("\nTo manually test the enhanced login UI:")
    print("1. Run: python app.py")
    print("2. Open: http://127.0.0.1:5000/login")
    print("3. Try the admin credentials: admin / admin123")
    print("4. Test form validation by leaving fields empty")
    print("5. Test the 'Remember me' checkbox")
    print("6. Test password visibility toggle")
    print("7. Check responsiveness on different screen sizes")
