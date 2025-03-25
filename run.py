"""
Application runner script.

This script is used to run the Flask application in development mode.
For production, use gunicorn or another WSGI server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 