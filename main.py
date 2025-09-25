#!/usr/bin/env python3
"""
Main entry point for the GitHub Repository Health Dashboard
This file serves as the production entry point for deployment
"""

from app import app

# Expose the Flask app instance for Gunicorn
if __name__ == '__main__':
    # For local development, you can still run python main.py
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)