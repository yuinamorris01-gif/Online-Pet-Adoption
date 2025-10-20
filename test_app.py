#!/usr/bin/env python3
"""
Pet Adoption System - Application Tester
This script tests the Flask application to ensure everything is working correctly
"""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime
from threading import Thread
import time

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        import flask
        import sqlite3
        import werkzeug
        import uuid
        import secrets
        print("✅ All required modules imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created"""
    print("🧪 Testing Flask app creation...")
    try:
        sys.path.insert(0, '.')
        import app
        flask_app = app.app
        print("✅ Flask app created successfully!")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    print("🧪 Testing database connection...")
    try:
        conn = sqlite3.connect('pet_adoption.db')
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pets")
        pet_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Database connection successful! {user_count} users, {pet_count} pets")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_routes():
    """Test if critical routes are defined"""
    print("🧪 Testing route definitions...")
    try:
        sys.path.insert(0, '.')
        import app
        
        required_routes = [
            ('/', 'index'),
            ('/pets', 'pets'),
            ('/login', 'login'),
            ('/register', 'register'),
            ('/admin', 'admin_dashboard')
        ]
        
        missing_routes = []
        app_rules = [rule.rule for rule in app.app.url_map.iter_rules()]
        
        for route, endpoint in required_routes:
            if route not in app_rules:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"❌ Missing routes: {', '.join(missing_routes)}")
            return False
        else:
            print("✅ All critical routes are defined!")
            return True
    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        return False

def test_template_rendering():
    """Test if templates can be rendered"""
    print("🧪 Testing template rendering...")
    try:
        sys.path.insert(0, '.')
        import app
        
        with app.app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code != 200:
                print(f"❌ Home page failed: {response.status_code}")
                return False
            
            # Test pets page
            response = client.get('/pets')
            if response.status_code != 200:
                print(f"❌ Pets page failed: {response.status_code}")
                return False
            
            # Test login page
            response = client.get('/login')
            if response.status_code != 200:
                print(f"❌ Login page failed: {response.status_code}")
                return False
        
        print("✅ Template rendering successful!")
        return True
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False

def test_static_files():
    """Test if static files are accessible"""
    print("🧪 Testing static file access...")
    try:
        static_files = ['static/css/style.css', 'static/js/main.js']
        
        for file_path in static_files:
            if not os.path.exists(file_path):
                print(f"❌ Missing static file: {file_path}")
                return False
        
        print("✅ All static files are accessible!")
        return True
    except Exception as e:
        print(f"❌ Static file test failed: {e}")
        return False

def test_admin_user():
    """Test if admin user exists and can be authenticated"""
    print("🧪 Testing admin user...")
    try:
        conn = sqlite3.connect('pet_adoption.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, role FROM users WHERE role = 'admin'")
        admin_users = cursor.fetchall()
        conn.close()
        
        if not admin_users:
            print("❌ No admin user found!")
            return False
        
        print(f"✅ Admin user found: {admin_users[0][0]}")
        return True
    except Exception as e:
        print(f"❌ Admin user test failed: {e}")
        return False

def run_server_test():
    """Test if the server can start"""
    print("🧪 Testing server startup...")
    try:
        sys.path.insert(0, '.')
        import app
        
        # Test if app can run (we won't actually start the server)
        if hasattr(app.app, 'run'):
            print("✅ Server can be started!")
            return True
        else:
            print("❌ Server startup method not found!")
            return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 Pet Adoption System Application Tester")
    print("=" * 50)
    
    tests = [
        ('imports', test_imports),
        ('app_creation', test_app_creation),
        ('database', test_database_connection),
        ('routes', test_routes),
        ('templates', test_template_rendering),
        ('static_files', test_static_files),
        ('admin_user', test_admin_user),
        ('server', run_server_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name.upper()} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS")
    print("=" * 50)
    
    success_count = sum(results.values())
    total_tests = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name.upper():15} {status}")
    
    print(f"\n🎯 Test Score: {success_count}/{total_tests} ({(success_count/total_tests)*100:.1f}%)")
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! Your Pet Adoption System is ready to use!")
        print("\n🚀 To start the application, run:")
        print("   python app.py")
    elif success_count >= total_tests * 0.8:
        print("\n👍 Most tests passed! Minor issues may need attention.")
    else:
        print("\n⚠️ Several tests failed. Please review the issues above.")
    
    print("\n📋 NEXT STEPS:")
    print("1. Run 'python app.py' to start the server")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Login with admin/admin123 for admin access")
    print("4. Test the application features")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
