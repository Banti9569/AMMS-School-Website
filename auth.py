from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_helpers import authenticate_user, get_user_by_id, reset_user_password
from security import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('parent.dashboard'))
        
    role_tab = request.args.get('role', 'parent') # default to parent for mobile users
    
    if request.method == 'POST':
        login_type = request.form.get('login_type', 'parent')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both your identifier and password.', 'warning')
            return render_template('auth/login.html', role_tab=login_type)
            
        user = authenticate_user(username, password)
        if user:
            # Check role matches intended access or allow both
            if login_type == 'admin' and user['role'] != 'admin':
                flash('This account does not have administrator privileges.', 'danger')
                return render_template('auth/login.html', role_tab='admin')
                
            session.clear()
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            
            flash(f"Welcome back, {user['full_name']}!", 'success')
            
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
                
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('parent.dashboard'))
        else:
            flash('Invalid login credentials. Please check your mobile number or username and password.', 'danger')
            return render_template('auth/login.html', role_tab=login_type, username=username)
            
    return render_template('auth/login.html', role_tab=role_tab)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('public.home'))

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()
        flash('Password reset request received. For safety and child privacy, school administration will verify your registered phone and send an SMS or assist you directly.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')
