from flask import Flask, request, jsonify, redirect
import requests
from flask_cors import CORS


app = Flask(__name__)

# Enable CORS for all routes with specific settings
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# Define the base URLs for the authentication, feedback services, profile service, and chat service
AUTH_SERVICE = "http://3.27.236.52:5001/auth"
FEEDBACK_SERVICE = "http://3.27.30.71:5002/feedback"
PROFILE_SERVICE = "http://13.236.188.76:5003/profile"
CHAT_SERVICE = "http://3.106.122.148:5004/chat"

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


@app.route("/feedback/<path:path>", methods=["GET", "POST"])
def feedback_proxy(path):
    target_url = f"{FEEDBACK_SERVICE}/{path}"
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    data = request.get_json() if request.method == "POST" else None

    if request.method == "POST":
        response = requests.post(target_url, headers=headers, json=data)
    elif request.method == "GET":
        response = requests.get(target_url, headers=headers, params=request.args)

    response_data = response.json() if response.content else {}
    return jsonify(response_data), response.status_code


@app.route("/profile/upload-profile-picture", methods=["POST"])
def proxy_upload_profile_picture():
    headers = {'Authorization': request.headers.get('Authorization')}
    files = {'profile_pic': request.files['profile_pic']}
    target_url = f"{PROFILE_SERVICE}/upload-profile-picture"
    response = requests.post(target_url, headers=headers, files=files)
    return jsonify(response.json()), response.status_code


@app.route("/profile/download-profile-picture", methods=["GET"])
def proxy_download_profile_picture():
    headers = {'Authorization': request.headers.get('Authorization')}
    target_url = f"{PROFILE_SERVICE}/download-profile-picture"
    response = requests.get(target_url, headers=headers)
    return jsonify(response.json()), response.status_code


@app.route("/chat/query", methods=["POST"])
def proxy_chat_query():
    """Proxy endpoint that forwards chat queries to the chat service."""
    headers = {
        'Authorization': request.headers.get('Authorization'),
        'Content-Type': 'application/json'
    }
    data = request.get_json()  # Extract JSON payload from the request body

    # Target URL for the chat service
    target_url = f"{CHAT_SERVICE}/query"

    # Forward the POST request to the chat service
    response = requests.post(target_url, headers=headers, json=data)

    # Return the response from the chat service
    response_data = response.json() if response.content else {}
    return jsonify(response_data), response.status_code


if __name__ == "__main__":
     app.run(host="0.0.0.0", port=5000, ssl_context=('server.crt', 'server.key'))

