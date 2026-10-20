import os

# Load environment variables from .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Detect if running in Vercel or AWS Lambda serverless environment
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'al-majid-mission-school-secure-key-2026-hazipur')
    
    # Paths & Storage
    # In Vercel serverless functions, the project root is read-only; only /tmp is writable.
    IS_VERCEL = IS_VERCEL
    BASE_DIR = BASE_DIR
    
    if IS_VERCEL:
        _env_db = os.environ.get('DATABASE_PATH')
        DATABASE = _env_db if (_env_db and _env_db.startswith('/tmp')) else '/tmp/school.db'
        
        _env_upload = os.environ.get('UPLOAD_FOLDER')
        UPLOAD_FOLDER = _env_upload if (_env_upload and _env_upload.startswith('/tmp')) else '/tmp/uploads'
    else:
        _db_path = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'database', 'school.db'))
        DATABASE = _db_path if os.path.isabs(_db_path) else os.path.join(BASE_DIR, _db_path)
        
        _upload_folder = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'static', 'uploads'))
        UPLOAD_FOLDER = _upload_folder if os.path.isabs(_upload_folder) else os.path.join(BASE_DIR, _upload_folder)
    
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 16)) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Server / App Environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days
    
    # School Meta Information
    SCHOOL_NAME = os.environ.get('SCHOOL_NAME', "Al Majid Mission School")
    SCHOOL_TAGLINE = os.environ.get('SCHOOL_TAGLINE', "Nurturing Character, Fostering Knowledge, Inspiring Leadership")
    SCHOOL_ADDRESS = os.environ.get('SCHOOL_ADDRESS', "Hazipur, P.O. Hazipur, Dist. Murshidabad/Birbhum Border, West Bengal - 731245")
    SCHOOL_PHONE = os.environ.get('SCHOOL_PHONE', "+91 94340 56789, +91 98765 43210")
    SCHOOL_EMAIL = os.environ.get('SCHOOL_EMAIL', "info@almajidmissionschool.edu.in")
    SCHOOL_HOURS = os.environ.get('SCHOOL_HOURS', "Monday - Saturday: 8:00 AM - 3:30 PM (Friday: 8:00 AM - 12:00 PM)")
