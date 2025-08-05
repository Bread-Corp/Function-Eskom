import json
import requests
import logging
from models import EskomTender

# --- Configuration ---
ESKOM_API_URL = "https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID="
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
}
# Set up basic logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Fetches all available tenders from the Eskom API, deserializes them
    using the EskomTender model, and returns a clean JSON array of the results.
    This serves as a robust baseline for data transformation.
    """
    logger.info("Starting Eskom tender processing job.")

    # --- 1. Fetch ALL tenders from the API ---
    try:
        logger.info(f"Fetching data from {ESKOM_API_URL}")
        response = requests.get(ESKOM_API_URL, headers=HEADERS, timeout=30) # Increased timeout for large payload
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        api_data = response.json()
        logger.info(f"Successfully fetched {len(api_data)} tender items from the API.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from API: {e}")
        # In a real scenario, you might want to retry or raise the exception
        # For now, we return an error state.
        return {'statusCode': 502, 'body': json.dumps({'error': 'Failed to fetch data from source API'})}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from API response. Response text: {response.text}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Invalid JSON response from source API'})}


    # --- 2. Process each tender with robust error handling ---
    processed_tenders = []
    skipped_count = 0
    for item in api_data:
        try:
            # The from_api_response classmethod does all the heavy lifting.
            # If it fails, it will raise an exception.
            tender_object = EskomTender.from_api_response(item)
            processed_tenders.append(tender_object)

        except (KeyError, ValueError, TypeError) as e:
            # This block is crucial for data integrity.
            # It catches errors during an individual tender's processing
            # without stopping the entire batch.
            skipped_count += 1
            tender_id = item.get('TENDER_ID', 'Unknown')
            logger.warning(f"Skipping tender {tender_id} due to a validation/parsing error: {e}")
            continue # Move to the next item

    logger.info(f"Successfully processed {len(processed_tenders)} tenders.")
    if skipped_count > 0:
        logger.warning(f"Skipped a total of {skipped_count} tenders due to errors.")


    # --- 3. Serialize the final list of objects into dictionaries ---
    # This is the clean data that will eventually be sent to your RDS writer function.
    response_body = [tender.to_dict() for tender in processed_tenders]

    logger.info("Processing complete. Returning serialized data.")
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_body, indent=2) # indent for nice formatting in test console
    }