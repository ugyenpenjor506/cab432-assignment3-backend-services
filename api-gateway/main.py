from flask import Flask, request, jsonify, redirect, url_for
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Existing services
AUTH_SERVICE = "http://3.27.236.52:5001/auth"
FEEDBACK_SERVICE = "http://3.27.30.71:5002/feedback"
PROFILE_SERVICE = "http://13.236.188.76:5003/profile"
CHAT_SERVICE = "http://3.106.122.148:5004/chat"

# CloudFront URL
CLOUDFRONT_URL = "https://d26ajj5z9aer07.cloudfront.net"

# Example route for CloudFront-proxied static files
@app.route("/static/<path:filename>", methods=["GET"])
def proxy_static(filename):
    target_url = f"{CLOUDFRONT_URL}/{filename}"
    response = requests.get(target_url)

    # Return the content with the appropriate MIME type and status code
    return response.content, response.status_code, {'Content-Type': response.headers.get('Content-Type')}

# Other proxy routes remain unchanged
@app.route("/auth/<path:path>", methods=["GET", "POST"])
def auth_proxy(path):
    target_url = f"{AUTH_SERVICE}/{path}"
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    data = request.get_json() if request.method == "POST" else None

    if request.method == "POST":
        response = requests.post(target_url, headers=headers, json=data)
    elif request.method == "GET":
        response = requests.get(target_url, headers=headers, params=request.args)

    response_data = response.json() if response.content else {}
    return jsonify(response_data), response.status_code

# Other routes for feedback, profile, and chat services remain as defined in your existing code...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=('server.crt', 'server.key'))
