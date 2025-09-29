#!/usr/bin/env python3
"""
WSGI entry point for the supplier management system.
This file is used by Gunicorn to serve the application in production.
"""

import os
import sys

# Add the project directory to the Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app

# Set the environment to production
os.environ.setdefault('FLASK_ENV', 'production')

# Create the Flask application
application = create_app()
app = application  # For compatibility with some WSGI servers

if __name__ == "__main__":
    application.run()