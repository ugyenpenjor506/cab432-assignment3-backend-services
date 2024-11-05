from app import app
from app.service.ApiService import ApiService
from app.service.DatabaseService import DatabaseService
from flask import jsonify, request
from flask_cors import CORS
from app.helper.AuthHelper import token_required
import boto3
import json
import threading
import time

# Enable CORS for all routes
CORS(app)

# Initialize SQS client
sqs_client = boto3.client('sqs', region_name='ap-southeast-2')
queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/194722437060/chatservice-queue'

# Initialize services
apiService = ApiService()
databaseService = DatabaseService()

class ChatController:
    
    @app.route('/chat/response/<int:conversation_id>/<int:query_id>', methods=['GET'])
    @token_required
    def get_chat_response(current_user, conversation_id, query_id):
        # Retrieve the response from the database
        response = databaseService.get_response(conversation_id, query_id)
        if response is None:
            return jsonify({
                "status": "pending",
                "code": 202,
                "message": "The response is still being processed."
            }), 202
        
        return jsonify({
            "status": "success",
            "code": 200,
            "response": response
        }), 200

    @app.route('/chat/query', methods=['POST'], strict_slashes=False)
    @token_required  # Protect this route with either Google or custom token
    def chatQuery(current_user):
        data = request.get_json()  # Extract the request body data
        user_id = current_user  # The user ID from the token (Google or custom)

        if not user_id:
            return jsonify({
                "status": "error", 
                "code": 400, 
                "message": "User ID is required"
            }), 400

        # Use the user_id to create a conversation
        create_conversation = databaseService.create_conversation(user_id)
        
        if create_conversation is None:
            return jsonify({
                "status": "error", 
                "code": 500, 
                "message": "Failed to create conversation"
            }), 500

        user_input = data.get("query")  # Extract the user's query from the request body
        
        if not user_input:
            return jsonify({
                "status": "error", 
                "code": 400, 
                "message": "No query provided"
            }), 400

        # Create the query in the database with the ConversationID and user input
        create_query = databaseService.create_query(create_conversation.ConversationID, user_input)

        # Prepare the message for SQS
        message_body = {
            "user_id": user_id,
            "conversation_id": create_conversation.ConversationID,
            "query_id": create_query.QueryID,
            "user_input": user_input
        }

        try:
            # Send the message to the SQS queue
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body)  # Convert the message body to a JSON string
            )
        except Exception as e:
            return jsonify({
                "status": "error",
                "code": 500,
                "message": f"Failed to send message to SQS: {str(e)}"
            }), 500

        # Return a response indicating the message was queued
        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Your query has been successfully queued for processing.",
            "conversation_id": create_conversation.ConversationID,
            "query_id": create_query.QueryID
        }), 200

# Function to process messages from the SQS queue
def process_message(message):
    try:
        # Use the Flask application context
        with app.app_context():
            # Parse the message body
            body = json.loads(message['Body'])

            user_id = body['user_id']
            conversation_id = body['conversation_id']
            query_id = body['query_id']
            user_input = body['user_input']

            # Call the OpenAI API (or any long-running process) using the input
            openai_response = apiService.openai_api(user_input, conversation_id, query_id)

            # Check if 'response' exists in the OpenAI API response
            if "response" not in openai_response:
                print(f"Unexpected OpenAI API response format: {openai_response}")
                return False

            # Save the response in the database or perform further processing
            databaseService.create_response(conversation_id, query_id, openai_response["response"])

            print(f"Processed message for conversation_id: {conversation_id}, query_id: {query_id}")
            return True
    except Exception as e:
        print(f"Failed to process message: {str(e)}")
        return False

# Function to poll the SQS queue in a background thread
def poll_sqs_queue():
    while True:
        try:
            # Receive messages from the SQS queue
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,  # Adjust the number of messages to process in one batch
                WaitTimeSeconds=10  # Long polling to reduce the number of API requests
            )

            messages = response.get('Messages', [])

            if not messages:
                continue  # No messages, continue polling

            for message in messages:
                if process_message(message):
                    # If the message was processed successfully, delete it from the queue
                    sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                else:
                    print(f"Failed to process message: {message['MessageId']}")

        except Exception as e:
            print(f"Error while polling the SQS queue: {str(e)}")
            time.sleep(5)  # Wait for a while before retrying

# Start the SQS worker in a background thread when the Flask app starts
worker_thread = threading.Thread(target=poll_sqs_queue)
worker_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
worker_thread.start()

# Instantiate the controller to ensure the route is registered
apiService = ApiService()
databaseService = DatabaseService()
