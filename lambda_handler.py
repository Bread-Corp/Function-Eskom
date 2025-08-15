"""
This module contains the AWS Lambda function handler for fetching and processing
tender data from the Eskom Tender Bulletin API.

The main function, lambda_handler, orchestrates the process of:
1.  Making an HTTP GET request to the Eskom API to retrieve a list of all tenders.
2.  Parsing the JSON response.
3.  Iterating through each tender item and transforming it into a structured
    `EskomTender` object using the data models defined in `models.py`.
4.  Handling potential errors during the API request or data processing, such as
    network issues, invalid JSON, or missing/malformed data fields.
5.  Serializing the processed tender objects back into a JSON format.
6.  Returning the final JSON data in a format compatible with Amazon API Gateway.
"""

import json
import requests # Add layer in AWS console.
import logging
from models import EskomTender

# --- Configuration ---

# The URL for the Eskom Tender Bulletin API.
# This endpoint is expected to return a JSON array of all available tenders.
ESKOM_API_URL = "https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID="

# Standard headers to mimic a web browser. This can help prevent being blocked
# by APIs that might reject requests from non-browser clients.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
}

# Initialize the logger. Using logging is best practice for serverless functions
# as it integrates with AWS CloudWatch for monitoring and debugging.
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda function handler to fetch, process, and return tender data.

    This function is the entry point for the Lambda execution. It fetches tender
    data from the Eskom API, processes each tender using the `EskomTender` model,
    and returns a structured JSON response.

    Args:
        event (dict): The event dictionary passed by AWS Lambda. It contains
                      invocation details, such as request parameters from API
                      Gateway. This function does not use this parameter.
        context (object): The context object passed by AWS Lambda. It provides
                          runtime information about the invocation, function,
                          and execution environment. This function does not use
                          this parameter.

    Returns:
        dict: A dictionary formatted for an API Gateway proxy response.
              On success, it contains a statusCode of 200 and a JSON string
              body with the tender data. On failure (e.g., API fetch error),
              it returns a 502 (Bad Gateway) status code with an error message.
    """
    logger.info("Starting Eskom tender processing job.")

    # --- Step 1: Fetch all tenders from the API ---
    try:
        logger.info(f"Fetching data from {ESKOM_API_URL}")
        # Make the GET request with a 30-second timeout.
        response = requests.get(ESKOM_API_URL, headers=HEADERS, timeout=30)
        # Raise an HTTPError for bad responses (4xx or 5xx).
        response.raise_for_status()
        # Decode the JSON response into a Python list.
        api_data = response.json()
        logger.info(f"Successfully fetched {len(api_data)} tender items from the API.")

    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., DNS failure, connection timeout).
        logger.error(f"Failed to fetch data from API: {e}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Failed to fetch data from source API'})}
    except json.JSONDecodeError:
        # Handle cases where the API returns a non-JSON response.
        logger.error(f"Failed to decode JSON from API response. Response text: {response.text}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Invalid JSON response from source API'})}

    # --- Step 2: Process each tender with robust error handling ---
    processed_tenders = []
    skipped_count = 0
    for item in api_data:
        try:
            # Use the factory method from the model to create a validated and cleaned object.
            tender_object = EskomTender.from_api_response(item)
            processed_tenders.append(tender_object)

        except (KeyError, ValueError, TypeError) as e:
            # Catch potential errors during object creation, such as a missing required
            # field ('TENDER_ID'), an invalid date format, or other data inconsistencies.
            skipped_count += 1
            tender_id = item.get('TENDER_ID', 'Unknown')
            logger.warning(f"Skipping tender {tender_id} due to a validation/parsing error: {e}")
            continue  # Move to the next item in the loop.

    logger.info(f"Successfully processed {len(processed_tenders)} tenders.")
    if skipped_count > 0:
        logger.warning(f"Skipped a total of {skipped_count} tenders due to errors.")

    # --- Step 3: Serialize the final list of objects into dictionaries ---
    # Convert each EskomTender object into a dictionary suitable for JSON serialization.
    response_body = [tender.to_dict() for tender in processed_tenders]

    logger.info("Processing complete. Returning serialized data.")
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_body, indent=2)  # Use indent for pretty-printing.
    }