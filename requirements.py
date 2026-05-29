"""
Freelancer Time and Invoice Management System
Requirements and Dependencies

This file documents all required packages and their versions for running this application.
Python version: 3.8 or higher

Installation Instructions:
1. Create a virtual environment: python -m venv venv
2. Activate the virtual environment:
   - Windows: venv\Scripts\activate
   - Linux/Mac: source venv/bin/activate
3. Install dependencies: pip install -r requirements.txt

Or install using pip directly:
pip install Flask==2.3.3 Werkzeug==2.3.7
"""

# Core Framework
Flask==2.3.3  # Web framework for building the application
Werkzeug==2.3.7  # WSGI utilities for Flask

# Database
# SQLite is built-in with Python, no additional package needed

# Additional utilities (optional but recommended)
python-dotenv==1.0.0  # For environment variable management (optional)
