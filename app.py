from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import secrets
from dotenv import load_dotenv
import webbrowser
import threading

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load environment variables or use defaults
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom template filter for datetime formatting
@app.template_filter('strftime')
def datetime_filter(dt, format='%B %d, %Y at %I:%M %p'):
    """Convert datetime to formatted string"""
    if isinstance(dt, str):
        # Parse datetime string if needed
        try:
            dt = datetime.fromisoformat(dt)
        except (ValueError, TypeError):
            return dt  # Return original if can't parse
    if hasattr(dt, 'strftime'):
        return dt.strftime(format)
    return dt

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('pet_adoption.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'adopter',
            full_name TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            size TEXT NOT NULL,
            description TEXT,
            special_needs TEXT,
            vaccination_status TEXT,
            photo_filename TEXT,
            location TEXT,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Adoption applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adoption_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pet_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            application_text TEXT,
            housing_type TEXT,
            has_other_pets BOOLEAN,
            other_pets_description TEXT,
            experience_with_pets TEXT,
            reason_for_adoption TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            admin_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (pet_id) REFERENCES pets (id)
        )
    ''')
    
    # Password reset tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin user if it doesn't exist
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    if cursor.fetchone()[0] == 0:
        admin_password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@petadoption.com', admin_password_hash, 'admin', 'System Administrator'))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('pet_adoption.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Home page with featured pets"""
    conn = get_db_connection()
    featured_pets = conn.execute('''
        SELECT * FROM pets WHERE status = 'available' 
        ORDER BY created_at DESC LIMIT 6
    ''').fetchall()
    conn.close()
    return render_template('index.html', pets=featured_pets)

@app.route('/sitemap')
def sitemap():
    """Site navigation map page"""
    return render_template('sitemap.html')

@app.route('/pets')
def pets():
    """Pet listing page with search and filter"""
    species = request.args.get('species', '')
    breed = request.args.get('breed', '')
    age_min = request.args.get('age_min', '')
    age_max = request.args.get('age_max', '')
    size = request.args.get('size', '')
    location = request.args.get('location', '')
    
    conn = get_db_connection()
    
    query = "SELECT * FROM pets WHERE status = 'available'"
    params = []
    
    if species:
        query += " AND species LIKE ?"
        params.append(f'%{species}%')
    if breed:
        query += " AND breed LIKE ?"
        params.append(f'%{breed}%')
    if age_min:
        query += " AND age >= ?"
        params.append(age_min)
    if age_max:
        query += " AND age <= ?"
        params.append(age_max)
    if size:
        query += " AND size = ?"
        params.append(size)
    if location:
        query += " AND location LIKE ?"
        params.append(f'%{location}%')
    
    query += " ORDER BY created_at DESC"
    
    pets_list = conn.execute(query, params).fetchall()
    
    # Get unique values for filters
    all_species = conn.execute("SELECT DISTINCT species FROM pets ORDER BY species").fetchall()
    all_breeds = conn.execute("SELECT DISTINCT breed FROM pets ORDER BY breed").fetchall()
    all_sizes = conn.execute("SELECT DISTINCT size FROM pets ORDER BY size").fetchall()
    all_locations = conn.execute("SELECT DISTINCT location FROM pets ORDER BY location").fetchall()
    
    conn.close()
    
    return render_template('pets.html', 
                         pets=pets_list,
                         species_list=all_species,
                         breeds_list=all_breeds,
                         sizes_list=all_sizes,
                         locations_list=all_locations,
                         filters={
                             'species': species,
                             'breed': breed,
                             'age_min': age_min,
                             'age_max': age_max,
                             'size': size,
                             'location': location
                         })

@app.route('/pet/<int:pet_id>')
def pet_detail(pet_id):
    """Individual pet detail page"""
    conn = get_db_connection()
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    conn.close()
    
    if pet is None:
        flash('Pet not found.', 'error')
        return redirect(url_for('pets'))
    
    return render_template('pet_detail.html', pet=pet)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (username, email, password_hash, full_name, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, phone, address))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/simple-login')
def simple_login():
    """Simple login page for testing"""
    return render_template('simple_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Basic validation
        if not username:
            flash('Please enter your username or email.', 'error')
            return render_template('login.html')
            
        if not password:
            flash('Please enter your password.', 'error')
            return render_template('login.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('login.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            user = conn.execute(
                'SELECT * FROM users WHERE username = ? OR email = ?',
                (username, username)
            ).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                # Handle "Remember Me" functionality
                remember_me = request.form.get('remember_me')
                if remember_me:
                    # Extend session to 30 days
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(days=30)
                else:
                    # Default session timeout (browser session)
                    session.permanent = False
                
                flash(f'Welcome back, {user["full_name"] or user["username"]}!', 'success')
                
                # Redirect to requested page or dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                
                # Redirect admin users to admin dashboard, regular users to home
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                # Check if user exists (for better error messaging)
                conn = get_db_connection()
                existing_user = conn.execute(
                    'SELECT id FROM users WHERE username = ? OR email = ?',
                    (username, username)
                ).fetchone()
                conn.close()
                
                if existing_user:
                    flash('Incorrect password. Please try again.', 'error')
                else:
                    flash('No account found with that username or email.', 'error')
                    
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
            print(f"Login error: {e}")  # For debugging
    
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT id, email FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            # Generate a unique token
            token = str(uuid.uuid4())
            # Set token expiration (e.g., 1 hour from now)
            expires_at = datetime.now() + timedelta(hours=1)
            
            conn.execute('INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
                         (user['id'], token, expires_at))
            conn.commit()
            
            # In a real application, you would send an email here
            # For this demo, we'll just flash a message with the reset link
            reset_link = url_for('reset_password', token=token, _external=True)
            flash(f'A password reset link has been sent to your email. Click here to reset: {reset_link}', 'info')
        else:
            flash('No account found with that email address.', 'error')
            
        conn.close()
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    conn = get_db_connection()
    reset_record = conn.execute(
        'SELECT user_id, expires_at FROM password_reset_tokens WHERE token = ?',
        (token,)
    ).fetchone()
    
    if not reset_record or datetime.fromisoformat(reset_record['expires_at']) < datetime.now():
        flash('Invalid or expired reset token.', 'error')
        conn.close()
        return redirect(url_for('forgot_password'))
        
    user_id = reset_record['user_id']
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            conn.close()
            return render_template('reset_password.html', token=token)
            
        # Update user's password
        hashed_password = generate_password_hash(new_password)
        conn.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                     (hashed_password, user_id))
        
        # Invalidate the token after use
        conn.execute('DELETE FROM password_reset_tokens WHERE token = ?', (token,))
        conn.commit()
        conn.close()
        
        flash('Your password has been reset successfully. Please log in.', 'success')
        return redirect(url_for('login'))
        
    conn.close()
    return render_template('reset_password.html', token=token)

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def adopt(pet_id):
    """Adoption application form"""
    if session.get('role') == 'admin':
        flash('Administrators cannot submit adoption applications.', 'error')
        return redirect(url_for('pet_detail', pet_id=pet_id))
    
    conn = get_db_connection()
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    
    if not pet or pet['status'] != 'available':
        flash('This pet is not available for adoption.', 'error')
        conn.close()
        return redirect(url_for('pets'))
    
    # Check if user already has a pending application for this pet
    existing_app = conn.execute('''
        SELECT id FROM adoption_applications 
        WHERE user_id = ? AND pet_id = ? AND status = 'pending'
    ''', (session['user_id'], pet_id)).fetchone()
    
    if existing_app:
        flash('You already have a pending application for this pet.', 'error')
        conn.close()
        return redirect(url_for('pet_detail', pet_id=pet_id))
    
    if request.method == 'POST':
        application_data = {
            'housing_type': request.form['housing_type'],
            'has_other_pets': request.form.get('has_other_pets') == 'on',
            'other_pets_description': request.form.get('other_pets_description', ''),
            'experience_with_pets': request.form['experience_with_pets'],
            'reason_for_adoption': request.form['reason_for_adoption'],
            'application_text': request.form.get('additional_info', '')
        }
        
        conn.execute('''
            INSERT INTO adoption_applications 
            (user_id, pet_id, housing_type, has_other_pets, other_pets_description,
             experience_with_pets, reason_for_adoption, application_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], pet_id, application_data['housing_type'],
              application_data['has_other_pets'], application_data['other_pets_description'],
              application_data['experience_with_pets'], application_data['reason_for_adoption'],
              application_data['application_text']))
        conn.commit()
        conn.close()
        
        flash('Your adoption application has been submitted successfully!', 'success')
        return redirect(url_for('my_applications'))
    
    conn.close()
    return render_template('adopt.html', pet=pet)

@app.route('/my-applications')
@login_required
def my_applications():
    """User's adoption applications"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_applications'))
    
    conn = get_db_connection()
    applications = conn.execute('''
        SELECT a.*, p.name as pet_name, p.species, p.breed, p.photo_filename
        FROM adoption_applications a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.user_id = ?
        ORDER BY a.submitted_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('my_applications.html', applications=applications)

@app.route('/adopt-info')
def adopt_info():
    """Adopt info page with pet browsing and filtering"""
    species = request.args.get('species', '')
    breed = request.args.get('breed', '')
    age_min = request.args.get('age_min', '')
    age_max = request.args.get('age_max', '')
    size = request.args.get('size', '')
    location = request.args.get('location', '')

    conn = get_db_connection()
    query = "SELECT * FROM pets WHERE status = 'available'"
    params = []
    if species:
        query += " AND species LIKE ?"
        params.append(f'%{species}%')
    if breed:
        query += " AND breed LIKE ?"
        params.append(f'%{breed}%')
    if age_min:
        query += " AND age >= ?"
        params.append(age_min)
    if age_max:
        query += " AND age <= ?"
        params.append(age_max)
    if size:
        query += " AND size = ?"
        params.append(size)
    if location:
        query += " AND location LIKE ?"
        params.append(f'%{location}%')
    query += " ORDER BY created_at DESC"
    pets_list = conn.execute(query, params).fetchall()
    all_species = conn.execute("SELECT DISTINCT species FROM pets ORDER BY species").fetchall()
    all_breeds = conn.execute("SELECT DISTINCT breed FROM pets ORDER BY breed").fetchall()
    all_sizes = conn.execute("SELECT DISTINCT size FROM pets ORDER BY size").fetchall()
    all_locations = conn.execute("SELECT DISTINCT location FROM pets ORDER BY location").fetchall()
    conn.close()
    return render_template('adopt_info.html',
                          pets=pets_list,
                          species_list=all_species,
                          breeds_list=all_breeds,
                          sizes_list=all_sizes,
                          locations_list=all_locations,
                          filters={
                              'species': species,
                              'breed': breed,
                              'age_min': age_min,
                              'age_max': age_max,
                              'size': size,
                              'location': location
                          })

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    stats = {
        'total_pets': conn.execute('SELECT COUNT(*) FROM pets').fetchone()[0],
        'available_pets': conn.execute('SELECT COUNT(*) FROM pets WHERE status = "available"').fetchone()[0],
        'pending_applications': conn.execute('SELECT COUNT(*) FROM adoption_applications WHERE status = "pending"').fetchone()[0],
        'total_users': conn.execute('SELECT COUNT(*) FROM users WHERE role = "adopter"').fetchone()[0]
    }
    
    recent_applications = conn.execute('''
        SELECT a.*, p.name as pet_name, u.full_name as applicant_name, u.email as applicant_email
        FROM adoption_applications a
        JOIN pets p ON a.pet_id = p.id
        JOIN users u ON a.user_id = u.id
        WHERE a.status = 'pending'
        ORDER BY a.submitted_at DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    return render_template('admin_dashboard.html', stats=stats, recent_applications=recent_applications)

@app.route('/admin/pets')
@admin_required
def admin_pets():
    """Admin pet management"""
    conn = get_db_connection()
    pets = conn.execute('SELECT * FROM pets ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_pets.html', pets=pets)

@app.route('/admin/pet/add', methods=['GET', 'POST'])
@admin_required
def admin_add_pet():
    """Add new pet"""
    if request.method == 'POST':
        # Handle file upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                # Add unique identifier to prevent conflicts
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                photo_filename = unique_filename
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO pets (name, species, breed, age, gender, size, description,
                            special_needs, vaccination_status, photo_filename, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form['species'],
            request.form['breed'],
            request.form['age'],
            request.form['gender'],
            request.form['size'],
            request.form['description'],
            request.form.get('special_needs', ''),
            request.form['vaccination_status'],
            photo_filename,
            request.form['location']
        ))
        conn.commit()
        conn.close()
        
        flash('Pet added successfully!', 'success')
        return redirect(url_for('admin_pets'))
    
    return render_template('admin_add_pet.html')

@app.route('/admin/pet/<int:pet_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_pet(pet_id):
    """Edit existing pet"""
    conn = get_db_connection()
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    
    if not pet:
        flash('Pet not found.', 'error')
        conn.close()
        return redirect(url_for('admin_pets'))
    
    if request.method == 'POST':
        photo_filename = pet['photo_filename']  # Keep existing photo by default
        
        # Handle new photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                
                # Delete old photo if it exists
                if photo_filename:
                    old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                photo_filename = unique_filename
        
        conn.execute('''
            UPDATE pets SET name=?, species=?, breed=?, age=?, gender=?, size=?,
                          description=?, special_needs=?, vaccination_status=?, 
                          photo_filename=?, location=?, status=?
            WHERE id=?
        ''', (
            request.form['name'],
            request.form['species'],
            request.form['breed'],
            request.form['age'],
            request.form['gender'],
            request.form['size'],
            request.form['description'],
            request.form.get('special_needs', ''),
            request.form['vaccination_status'],
            photo_filename,
            request.form['location'],
            request.form['status'],
            pet_id
        ))
        conn.commit()
        conn.close()
        
        flash('Pet updated successfully!', 'success')
        return redirect(url_for('admin_pets'))
    
    conn.close()
    return render_template('admin_edit_pet.html', pet=pet)

@app.route('/admin/pet/<int:pet_id>/delete', methods=['POST'])
@admin_required
def admin_delete_pet(pet_id):
    """Delete pet"""
    conn = get_db_connection()
    pet = conn.execute('SELECT photo_filename FROM pets WHERE id = ?', (pet_id,)).fetchone()
    
    if pet:
        # Delete photo file if it exists
        if pet['photo_filename']:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], pet['photo_filename'])
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        # Delete pet record
        conn.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
        conn.commit()
        flash('Pet deleted successfully!', 'success')
    else:
        flash('Pet not found.', 'error')
    
    conn.close()
    return redirect(url_for('admin_pets'))

@app.route('/admin/applications')
@admin_required
def admin_applications():
    """Admin application management"""
    status_filter = request.args.get('status', 'all')
    
    conn = get_db_connection()
    
    query = '''
        SELECT a.*, p.name as pet_name, p.species, p.breed,
               u.full_name as applicant_name, u.email as applicant_email, u.phone as applicant_phone
        FROM adoption_applications a
        JOIN pets p ON a.pet_id = p.id
        JOIN users u ON a.user_id = u.id
    '''
    params = []
    
    if status_filter != 'all':
        query += ' WHERE a.status = ?'
        params.append(status_filter)
    
    query += ' ORDER BY a.submitted_at DESC'
    
    applications = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_applications.html', applications=applications, status_filter=status_filter)

@app.route('/admin/application/<int:app_id>')
@admin_required
def admin_application_detail(app_id):
    """View application details"""
    conn = get_db_connection()
    application = conn.execute('''
        SELECT a.*, p.name as pet_name, p.species, p.breed, p.photo_filename,
               u.full_name as applicant_name, u.email as applicant_email, 
               u.phone as applicant_phone, u.address as applicant_address
        FROM adoption_applications a
        JOIN pets p ON a.pet_id = p.id
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    ''', (app_id,)).fetchone()
    conn.close()
    
    if not application:
        flash('Application not found.', 'error')
        return redirect(url_for('admin_applications'))
    
    return render_template('admin_application_detail.html', application=application)

@app.route('/admin/application/<int:app_id>/review', methods=['POST'])
@admin_required
def admin_review_application(app_id):
    """Approve or deny application"""
    action = request.form['action']
    admin_notes = request.form.get('admin_notes', '')
    
    if action not in ['approve', 'deny']:
        flash('Invalid action.', 'error')
        return redirect(url_for('admin_application_detail', app_id=app_id))
    
    conn = get_db_connection()
    
    # Get application details
    application = conn.execute('''
        SELECT pet_id FROM adoption_applications WHERE id = ?
    ''', (app_id,)).fetchone()
    
    if not application:
        flash('Application not found.', 'error')
        conn.close()
        return redirect(url_for('admin_applications'))
    
    # Update application status
    new_status = 'approved' if action == 'approve' else 'denied'
    conn.execute('''
        UPDATE adoption_applications 
        SET status = ?, admin_notes = ?, reviewed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_status, admin_notes, app_id))
    
    # If approved, mark pet as adopted and deny other pending applications
    if action == 'approve':
        pet_id = application['pet_id']
        conn.execute('UPDATE pets SET status = "adopted" WHERE id = ?', (pet_id,))
        
        # Deny other pending applications for this pet
        conn.execute('''
            UPDATE adoption_applications 
            SET status = 'denied', admin_notes = 'Pet adopted by another applicant'
            WHERE pet_id = ? AND status = 'pending' AND id != ?
        ''', (pet_id, app_id))
    
    conn.commit()
    conn.close()
    
    flash(f'Application {new_status} successfully!', 'success')
    return redirect(url_for('admin_applications'))

if __name__ == '__main__':
    init_db()
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')
    threading.Timer(1.5, open_browser).start()  # Delay to let the server start
    app.run(debug=True)
