import boto3
import json
import time
from app.service.ApiService import ApiService
from app.service.DatabaseService import DatabaseService

# Initialize SQS client
sqs_client = boto3.client('sqs', region_name='ap-southeast-2')
queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/194722437060/chatservice-queue'

# Initialize services
apiService = ApiService()
databaseService = DatabaseService()

def process_message(message):
    try:
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
        # Example: Save response in the database
        databaseService.save_response(conversation_id, query_id, openai_response["response"])

        print(f"Processed message for conversation_id: {conversation_id}, query_id: {query_id}")
        return True
    except Exception as e:
        print(f"Failed to process message: {str(e)}")
        return False

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

if __name__ == "__main__":
    print("Starting SQS message consumer...")
    poll_sqs_queue()
