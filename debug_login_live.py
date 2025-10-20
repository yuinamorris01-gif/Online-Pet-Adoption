#!/usr/bin/env python3
"""
Live login debugging - shows what happens when you submit a login
"""
import requests
import sys

def test_live_login():
    print("=== LIVE LOGIN DEBUG ===\n")
    
    # Test the simple login page first
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Check if app is running
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ App is running")
        else:
            print(f"❌ App not responding (status: {response.status_code})")
            return
    except requests.exceptions.ConnectionError:
        print("❌ App not running! Start it with: python app.py")
        return
    except Exception as e:
        print(f"❌ Error connecting to app: {e}")
        return
    
    # Test simple login page
    try:
        session = requests.Session()
        
        print(f"\n=== TESTING SIMPLE LOGIN PAGE ===")
        simple_login_url = f"{base_url}/simple-login"
        response = session.get(simple_login_url)
        
        if response.status_code == 200:
            print("✅ Simple login page loads")
        else:
            print(f"❌ Simple login page error: {response.status_code}")
        
        # Now try to submit login
        print(f"\n=== SUBMITTING LOGIN CREDENTIALS ===")
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'remember_me': 'on'
        }
        
        print(f"Sending POST to: {base_url}/login")
        print(f"Data: {login_data}")
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ Login successful - got redirect!")
            print(f"Redirecting to: {response.headers.get('Location', 'Unknown')}")
            
            # Follow the redirect
            if 'Location' in response.headers:
                redirect_response = session.get(base_url + response.headers['Location'])
                print(f"Final page status: {redirect_response.status_code}")
                
                if "Welcome back" in redirect_response.text:
                    print("🎉 LOGIN SUCCESS! Found welcome message")
                else:
                    print("⚠️  Redirected but no welcome message found")
        
        elif response.status_code == 200:
            # Check for error messages in response
            if "Invalid username or password" in response.text:
                print("❌ LOGIN FAILED: Invalid credentials")
            elif "Please enter your username" in response.text:
                print("❌ LOGIN FAILED: Username required")
            elif "Please enter your password" in response.text:
                print("❌ LOGIN FAILED: Password required")
            elif "Username must be at least" in response.text:
                print("❌ LOGIN FAILED: Username too short")
            elif "Password must be at least" in response.text:
                print("❌ LOGIN FAILED: Password too short")
            else:
                print("❌ LOGIN FAILED: Unknown error")
                print("Response contains flash messages or validation errors")
        
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
    
    print(f"\n=== MANUAL TESTING INSTRUCTIONS ===")
    print(f"1. Open browser and go to: {base_url}/simple-login")
    print(f"2. The form should be pre-filled with admin/admin123")
    print(f"3. Click the 'Login' button")
    print(f"4. You should be redirected to the home page")
    print(f"5. If not working, open browser dev tools (F12) and check Console tab for errors")
    
    print(f"\nAlternatively try the main login:")
    print(f"1. Go to: {base_url}/login") 
    print(f"2. Type exactly: admin")
    print(f"3. Type exactly: admin123")
    print(f"4. Click Sign In")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Installing requests module...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    test_live_login()
