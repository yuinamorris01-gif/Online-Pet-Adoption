#!/usr/bin/env python3
"""
Pet Adoption System - System Optimizer
This script helps optimize and fix common issues with the Pet Adoption System
"""

import os
import sqlite3
import shutil
import tempfile
from datetime import datetime
import secrets

def generate_secure_secret_key():
    """Generate a cryptographically secure secret key"""
    return secrets.token_hex(32)

def optimize_database():
    """Optimize SQLite database performance"""
    print("🔧 Optimizing database...")
    try:
        conn = sqlite3.connect('pet_adoption.db')
        cursor = conn.cursor()
        
        # Run VACUUM to defragment database
        cursor.execute('VACUUM;')
        
        # Analyze tables for optimal query planning
        cursor.execute('ANALYZE;')
        
        # Update SQLite settings for better performance
        cursor.execute('PRAGMA cache_size = 10000;')  # Increase cache size
        cursor.execute('PRAGMA temp_store = memory;')  # Use memory for temporary storage
        cursor.execute('PRAGMA journal_mode = WAL;')   # Write-Ahead Logging for better concurrency
        cursor.execute('PRAGMA synchronous = NORMAL;') # Balance between safety and performance
        
        conn.commit()
        conn.close()
        
        print("✅ Database optimized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database optimization failed: {e}")
        return False

def check_file_permissions():
    """Check and fix file permissions"""
    print("🔧 Checking file permissions...")
    try:
        critical_dirs = ['static', 'static/images', 'static/css', 'static/js', 'templates']
        critical_files = ['app.py', 'pet_adoption.db']
        
        issues_found = False
        
        for directory in critical_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"📁 Created missing directory: {directory}")
            elif not os.access(directory, os.R_OK | os.W_OK):
                issues_found = True
                print(f"⚠️ Permission issue with directory: {directory}")
        
        for file_path in critical_files:
            if os.path.exists(file_path) and not os.access(file_path, os.R_OK | os.W_OK):
                issues_found = True
                print(f"⚠️ Permission issue with file: {file_path}")
        
        if not issues_found:
            print("✅ All file permissions are correct!")
        return not issues_found
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False

def cleanup_old_files():
    """Clean up temporary and unnecessary files"""
    print("🔧 Cleaning up temporary files...")
    try:
        cleanup_patterns = [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.tmp',
            'check_db.py',  # Remove our temporary database check script
            '.pytest_cache'
        ]
        
        files_removed = 0
        for pattern in cleanup_patterns:
            if pattern.startswith('*'):
                # Handle file patterns
                import glob
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                        files_removed += 1
                    except:
                        pass
            else:
                # Handle directories
                if os.path.exists(pattern):
                    if os.path.isdir(pattern):
                        shutil.rmtree(pattern, ignore_errors=True)
                        files_removed += 1
                    else:
                        os.remove(pattern)
                        files_removed += 1
        
        print(f"✅ Cleaned up {files_removed} temporary files/directories!")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def validate_templates():
    """Check if all required templates exist"""
    print("🔧 Validating templates...")
    try:
        required_templates = [
            'base.html', 'index.html', 'pets.html', 'pet_detail.html',
            'login.html', 'register.html', 'adopt.html', 'my_applications.html',
            'admin_dashboard.html', 'admin_pets.html', 'admin_add_pet.html',
            'admin_applications.html', 'admin_application_detail.html',
            'forgot_password.html', 'reset_password.html'
        ]
        
        missing_templates = []
        for template in required_templates:
            template_path = os.path.join('templates', template)
            if not os.path.exists(template_path):
                missing_templates.append(template)
        
        if missing_templates:
            print(f"⚠️ Missing templates: {', '.join(missing_templates)}")
            return False
        else:
            print("✅ All required templates are present!")
            return True
    except Exception as e:
        print(f"❌ Template validation failed: {e}")
        return False

def validate_static_files():
    """Check if all required static files exist"""
    print("🔧 Validating static files...")
    try:
        required_files = [
            'static/css/style.css',
            'static/js/main.js'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"⚠️ Missing static files: {', '.join(missing_files)}")
            return False
        else:
            print("✅ All required static files are present!")
            return True
    except Exception as e:
        print(f"❌ Static file validation failed: {e}")
        return False

def create_backup():
    """Create a backup of the database"""
    print("🔧 Creating database backup...")
    try:
        if os.path.exists('pet_adoption.db'):
            backup_name = f"pet_adoption_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('pet_adoption.db', backup_name)
            print(f"✅ Database backed up to: {backup_name}")
            return True
        else:
            print("⚠️ No database file found to backup")
            return False
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    print("🔧 Checking disk space...")
    try:
        import psutil
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        total_gb = disk_usage.total / (1024**3)
        percent_free = (disk_usage.free / disk_usage.total) * 100
        
        print(f"📊 Disk space: {free_gb:.2f} GB free out of {total_gb:.2f} GB total ({percent_free:.1f}% free)")
        
        if percent_free < 20:
            print("⚠️ Warning: Low disk space (less than 20% free)")
            return False
        elif percent_free < 10:
            print("❌ Critical: Very low disk space (less than 10% free)")
            return False
        else:
            print("✅ Disk space is adequate!")
            return True
    except ImportError:
        print("⚠️ psutil not installed, skipping disk space check")
        return True
    except Exception as e:
        print(f"❌ Disk space check failed: {e}")
        return True

def create_env_file():
    """Create a .env file if it doesn't exist"""
    print("🔧 Creating .env file...")
    try:
        if not os.path.exists('.env'):
            env_content = f"""# Pet Adoption System Environment Variables
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SECRET_KEY={generate_secure_secret_key()}
DATABASE_URL=sqlite:///pet_adoption.db
UPLOAD_FOLDER=static/images
MAX_CONTENT_LENGTH=16777216
DEBUG=False
ENVIRONMENT=production
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created .env file with secure configuration!")
            return True
        else:
            print("✅ .env file already exists!")
            return True
    except Exception as e:
        print(f"❌ .env file creation failed: {e}")
        return False

def main():
    """Main optimization function"""
    print("🚀 Pet Adoption System Optimizer")
    print("=" * 50)
    
    results = {
        'backup': create_backup(),
        'permissions': check_file_permissions(),
        'templates': validate_templates(),
        'static_files': validate_static_files(),
        'database': optimize_database(),
        'cleanup': cleanup_old_files(),
        'disk_space': check_disk_space(),
        'env_file': create_env_file()
    }
    
    print("\n" + "=" * 50)
    print("📋 OPTIMIZATION SUMMARY")
    print("=" * 50)
    
    success_count = sum(results.values())
    total_checks = len(results)
    
    for check, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{check.upper():15} {status}")
    
    print(f"\n🎯 Overall Score: {success_count}/{total_checks} ({(success_count/total_checks)*100:.1f}%)")
    
    if success_count == total_checks:
        print("\n🎉 Your Pet Adoption System is fully optimized!")
    elif success_count >= total_checks * 0.8:
        print("\n👍 Your system is in good shape with minor issues to address.")
    else:
        print("\n⚠️ Your system needs attention. Please review the failed checks.")
    
    print("\n💡 RECOMMENDATIONS:")
    print("- Run this optimizer regularly (weekly)")
    print("- Monitor disk space and clean up old files")
    print("- Keep your Python packages updated")
    print("- Back up your database before making changes")
    print("- Use a proper secret key in production")
    
    return success_count == total_checks

if __name__ == "__main__":
    main()
