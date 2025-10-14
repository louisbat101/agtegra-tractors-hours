#!/usr/bin/env python3
"""
WSGI application for Hostinger deployment
"""

import sys
import os

# Add the project directory to Python path
project_home = os.path.dirname(__file__)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app_flask import app

# WSGI application
application = app

if __name__ == "__main__":
    app.run(debug=False)