import json
import requests

from TenderBase import EskomTender

# --- CONFIGURATION ---
ESKOM_API_BASE_URL = "https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
}
# Define a default range to scan. In a real scenario, you'd manage the last scanned ID in a database.
DEFAULT_START_ID = 73470
DEFAULT_RANGE = 10 # Number of IDs to check from the start ID

def lambda_handler(event, context):
    """
    Fetches a range of Eskom tenders, deserializes them into EskomTender objects,
    and returns them as a JSON array.
    """
    print("Lambda execution started for Eskom tenders.")

    # Allow the range to be overridden by the invocation event, e.g., for scheduled tasks
    start_id = event.get('start_id', DEFAULT_START_ID)
    scan_range = event.get('range', DEFAULT_RANGE)
    end_id = start_id + scan_range

    print(f"Scanning for TENDER_IDs in range: {start_id} to {end_id - 1}")

    processed_tenders = []
    
    for tender_id in range(start_id, end_id):
        url = f"{ESKOM_API_BASE_URL}?TENDER_ID={tender_id}"
        print(f"Fetching tender ID: {tender_id} from {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10) # 10-second timeout

            # A 404 Not Found is expected for IDs that don't exist. We just skip them.
            if response.status_code == 404:
                print(f"Tender ID {tender_id} not found. Skipping.")
                continue

            # Handle other HTTP errors
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

            # The API returns a list with one item, or an empty list if no data
            response_data = response.json()
            if not isinstance(response_data, list) or not response_data:
                print(f"Tender ID {tender_id} returned empty or invalid data. Skipping.")
                continue
            
            api_item = response_data[0]
            
            # --- The core deserialization step ---
            # The from_api_response method handles all mapping and validation.
            tender_object = EskomTender.from_api_response(api_item)
            processed_tenders.append(tender_object)
            print(f"Successfully processed tender ID: {tender_id}, Number: {tender_object.tender_number}")

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Network or HTTP error for tender ID {tender_id}: {e}")
            # Continue to the next ID, don't fail the whole batch
            continue
        except json.JSONDecodeError as e:
            print(f"ERROR: Could not decode JSON for tender ID {tender_id}. Response text: {response.text}")
            continue
        except (KeyError, TypeError, ValueError) as e:
            # This catches errors during deserialization (e.g., missing key, wrong data type)
            print(f"ERROR: Data validation/mapping failed for tender ID {tender_id}: {e}")
            continue
        except Exception as e:
            # Catch-all for any other unexpected errors
            print(f"FATAL ERROR: An unexpected error occurred for tender ID {tender_id}: {e}")
            continue

    print(f"Processing complete. Successfully deserialized {len(processed_tenders)} tenders.")
    
    # Convert all processed tender objects to dictionaries for the JSON response
    response_body = [tender.to_dict() for tender in processed_tenders]

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_body)
    }

# --- Example of how to test locally ---
if __name__ == '__main__':
    # Simulate a Lambda event. You can pass a custom start_id.
    # The example ID 73478 from your document is used here.
    event = {'start_id': 73478, 'range': 1} 
    context = {}
    result = lambda_handler(event, context)
    
    print("\n--- LAMBDA RESULT ---")
    print(f"Status Code: {result['statusCode']}")
    # Pretty-print the JSON body
    parsed_body = json.loads(result['body'])
    print(json.dumps(parsed_body, indent=2))