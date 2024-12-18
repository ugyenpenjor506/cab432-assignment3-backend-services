from flask import Flask, request
from flask_cors import CORS  # Import CORS
from app import app


# Enable CORS for all routes
CORS(app)  

# Main application entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
