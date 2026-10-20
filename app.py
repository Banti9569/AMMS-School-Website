import os
from flask import Flask, render_template, session, request, flash, redirect, url_for, abort
from config import Config
from models import init_db, seed_data_if_empty
from security import generate_csrf_token, validate_csrf
from auth import auth_bp
from routes.public import public_bp
from routes.parent import parent_bp
from routes.admin import admin_bp
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required directories exist (safely catch Read-Only filesystem on serverless platforms)
    try:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'notices'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'staff'), exist_ok=True)
        os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    except OSError:
        pass

    # Initialize SQLite database & seed
    with app.app_context():
        init_db()
        seed_data_if_empty()

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(admin_bp)

    # CSRF check before request
    @app.before_request
    def check_csrf():
        if not validate_csrf():
            flash('Your session or security token expired. Please try submitting again.', 'danger')
            return redirect(request.referrer or url_for('public.home'))

    # Inject global variables & CSRF token to all templates
    @app.context_processor
    def inject_globals():
        return {
            'csrf_token': generate_csrf_token,
            'current_year': datetime.now().year,
            'school_name': Config.SCHOOL_NAME,
            'school_tagline': Config.SCHOOL_TAGLINE,
            'school_address': Config.SCHOOL_ADDRESS,
            'school_phone': Config.SCHOOL_PHONE,
            'school_email': Config.SCHOOL_EMAIL,
            'school_hours': Config.SCHOOL_HOURS,
            'user_role': session.get('role'),
            'user_name': session.get('full_name')
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('public/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('public/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('public/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
