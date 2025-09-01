# ==================================================================================================
#
# File: EskomLambda/lambda_handler.py
#
# Description:
# This script contains an AWS Lambda function designed to fetch tender data from the Eskom
# Tender Bulletin API. It processes the raw data, transforms it into a structured format
# using the EskomTender model, and then sends it to an Amazon SQS (Simple Queue Service)
# queue for further processing by a downstream service (e.g., an AI tagging service).
#
# The function performs the following steps:
# 1. Fetches tender data from the Eskom API endpoint.
# 2. Handles potential network errors or invalid API responses.
# 3. Iterates through each tender item in the response.
# 4. Validates and parses each item into a structured EskomTender object.
# 5. Skips and logs any items that fail validation.
# 6. Converts the processed tender objects into dictionaries.
# 7. Batches the tender data into groups of 10.
# 8. Sends each batch to a specified SQS FIFO queue.
# 9. Logs the outcome of the entire operation.
#
# ==================================================================================================

# --- Import necessary libraries ---
import json         # For serializing Python dictionaries to JSON strings.
import requests     # For making HTTP requests to the Eskom API.
import logging      # For logging information and errors.
import boto3        # The AWS SDK for Python, used to interact with SQS.
from models import EskomTender  # Import the data model for Eskom tenders.

# --- Global Constants and Configuration ---

# The URL of the Eskom Tender Bulletin API.
ESKOM_API_URL = "https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID="

# HTTP headers to mimic a web browser, which can help avoid being blocked by the API.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
}

# --- Logger Setup ---
# Get the default Lambda logger instance.
logger = logging.getLogger()
# Set the logging level to INFO, so messages of severity INFO, WARNING, ERROR, and CRITICAL will be recorded.
logger.setLevel(logging.INFO)

# --- AWS Service Client Initialization ---
# Create a boto3 client to interact with the SQS service.
sqs_client = boto3.client('sqs')
# The URL of the target SQS FIFO (First-In, First-Out) queue.
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo'

# ==================================================================================================
# Lambda Function Handler
# This is the main entry point for the AWS Lambda execution.
# ==================================================================================================
def lambda_handler(event, context):
    """
    The main handler function for the AWS Lambda.

    Args:
        event (dict): The event data passed to the Lambda function (e.g., from a trigger like CloudWatch Events).
        context (object): The runtime information of the Lambda function (e.g., request ID, memory limits).

    Returns:
        dict: A dictionary containing the HTTP status code and a JSON-formatted body,
              which is standard for Lambda proxy integrations with API Gateway.
    """
    print("Lambda execution started for Eskom tenders.")

    # --- Step 1: Fetch Data from the Eskom API ---
    try:
        logger.info(f"Fetching data from {ESKOM_API_URL}")
        # Make a GET request to the API with a 30-second timeout.
        response = requests.get(ESKOM_API_URL, headers=HEADERS, timeout=30)
        # Check if the request was successful (i.e., status code 2xx). If not, raise an HTTPError.
        response.raise_for_status()
        # Parse the JSON response body into a Python list of dictionaries.
        api_data = response.json()
        logger.info(f"Successfully fetched {len(api_data)} tender items from the API.")
    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., DNS failure, connection timeout).
        logger.error(f"Failed to fetch data from API: {e}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Failed to fetch data from source API'})}
    except json.JSONDecodeError:
        # Handle cases where the API response is not valid JSON.
        logger.error(f"Failed to decode JSON from API response. Response text: {response.text}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Invalid JSON response from source API'})}

    # --- Step 2: Process and Validate Each Tender Item ---
    processed_tenders = []  # A list to store the successfully processed EskomTender objects.
    skipped_count = 0       # A counter for tenders that could not be processed.

    # Loop through each item received from the API.
    for item in api_data:
        try:
            # Use the model's factory method to parse the raw dictionary into a structured object.
            # This step performs validation and data cleaning.
            tender_object = EskomTender.from_api_response(item)
            # If successful, add the object to our list.
            processed_tenders.append(tender_object)
        except (KeyError, ValueError, TypeError) as e:
            # Catch errors that occur during parsing, such as missing keys or invalid data types.
            skipped_count += 1
            # Get the tender ID for logging, defaulting to 'Unknown' if not found.
            tender_id = item.get('TENDER_ID', 'Unknown')
            logger.warning(f"Skipping tender {tender_id} due to a validation/parsing error: {e}")
            continue  # Move to the next item in the loop.

    logger.info(f"Successfully processed {len(processed_tenders)} tenders.")
    if skipped_count > 0:
        logger.warning(f"Skipped a total of {skipped_count} tenders due to errors.")

    # --- Step 3: Prepare Data for SQS ---
    # Convert the list of EskomTender objects into a list of dictionaries.
    processed_tender_dicts = [tender.to_dict() for tender in processed_tenders]

    # --- Step 4: Batch and Send Messages to SQS ---
    # SQS `send_message_batch` has a limit of 10 messages per call.
    batch_size = 10
    # Use a list comprehension to split the list of tenders into smaller "chunks" or "batches".
    message_batches = [
        processed_tender_dicts[i:i + batch_size]
        for i in range(0, len(processed_tender_dicts), batch_size)
    ]

    sent_count = 0  # A counter for the total number of messages successfully sent.
    # Iterate over each batch of tenders.
    for batch in message_batches:
        # Prepare the entries for the `send_message_batch` call.
        entries = []
        for i, tender_dict in enumerate(batch):
            entries.append({
                # 'Id' is a unique identifier for the message within the batch.
                'Id': f'tender_message_{i}_{sent_count}',
                # 'MessageBody' must be a string. We serialize the dictionary to a JSON string.
                'MessageBody': json.dumps(tender_dict),
                # 'MessageGroupId' is required for FIFO queues to group messages.
                # All messages with the same group ID are processed in order.
                'MessageGroupId': 'EskomTenderScrape'
            })

        # Send the batch to SQS inside a try-except block to handle potential sending failures.
        try:
            response = sqs_client.send_message_batch(
                QueueUrl=SQS_QUEUE_URL,
                Entries=entries
            )
            # Increment the counter by the number of messages that were successfully sent in this batch.
            sent_count += len(response.get('Successful', []))
            logger.info(f"Successfully sent a batch of {len(entries)} messages to SQS.")
        except Exception as e:
            # Log any errors that occur during the SQS call.
            logger.error(f"Failed to send a message batch to SQS: {e}")

    logger.info(f"Processing complete. Sent a total of {sent_count} messages to SQS.")

    # --- Step 5: Return a Success Response ---
    # This response is sent back to the invoker of the Lambda function.
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tender data processed and sent to SQS queue.'})
    }
