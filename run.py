"""
Al Majid Mission School - Entry Point
Hazipur, West Bengal 731245
"""
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  AL MAJID MISSION SCHOOL - WEB SERVER")
    print(f"  Location: {Config.SCHOOL_ADDRESS[:45]}...")
    print(f"  Portal URL: http://{Config.HOST}:{Config.PORT} (or http://127.0.0.1:{Config.PORT})")
    print(f"  Environment: {Config.FLASK_ENV} | Debug: {Config.DEBUG}")
    print("=" * 60)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
