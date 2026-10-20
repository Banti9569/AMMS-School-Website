"""
Vercel Serverless Function Entry Point for Flask
Al Majid Mission School Web Application
"""
import sys
import os

# Ensure the root project directory is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import the WSGI Flask application instance
from app import app
