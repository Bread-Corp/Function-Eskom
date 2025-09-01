# Eskom Tender Processing Lambda Service
## 1. Overview
This service contains an AWS Lambda function responsible for scraping tender information from the Eskom Tender Bulletin API. Its primary function is to fetch raw tender data, process and validate it against a defined data model, and then dispatch it as messages to an Amazon SQS (Simple Queue Service) queue for further downstream processing.

The key goal of this service is to act as the first step in a data pipeline, ensuring that only clean, structured, and valid tender data is passed along.

## 2. Lambda Function (`lambda_handler.py`)
The `lambda_handler` is the main entry point for the service. It executes the following logic:
1. **Fetch Data**: It sends an HTTP GET request to the Eskom Tender Bulletin API.
2. **Error Handling**: It includes robust error handling for network issues (e.g., timeouts, connection errors) and invalid API responses (e.g., non-JSON content).
3. **Data Parsing**: It iterates through the list of tenders returned by the API. Each tender (a JSON object) is passed to the `EskomTender` model for parsing and validation.
4. **Validation & Logging**: If a tender fails validation (e.g., missing a required field or having a malformed date), it is skipped, and a warning is logged in CloudWatch for monitoring and debugging.
5. **Batching**: The successfully processed tenders are grouped into batches of 10. This is done to comply with the SQS `SendMessageBatch` API limit.
6. **Queueing**: Each batch of tender data is sent to the `AIQueue.fifo` SQS queue. A   `MessageGroupId` of `EskomTenderScrape` is used to ensure that all tenders from a single execution are processed in the order they were received within the FIFO queue.

## 3. Data Model (`models.py`)
The service uses a set of Python classes to define the structure of the tender data. This ensures consistency and makes the data easy to work with.

`TenderBase` **(Abstract Class)**
This is a foundational class that defines the common attributes for any tender, regardless of its source. It cannot be used directly but serves as a template for more specific tender classes.
- Core Attributes:
    - `title`: The title of the tender.
    - `description`: A detailed description.
    - `source`: The origin of the tender (hardcoded to `"Eskom"`).
    - `published_date`: The date the tender was published.
    - `closing_date`: The submission deadline.
    - `supporting_docs`: A list of `SupportingDoc` objects.
    - `tags`: A list of keywords or categories.

`EskomTender` **(Concrete Class)**
This class inherits from `TenderBase` and adds fields that are specific to the data provided by the Eskom API.
- **Inherited Attributes**: All attributes from `TenderBase`.
- **Eskom-Specific Attributes**:
    - `tender_number`: The unique ID from Eskom (populated from the REFERENCE field in the API).
    - `audience`: The intended audience for the tender.
    - `office_location`: The physical office location.
    - `email`: Contact email address.
    - `address`: Physical address for inquiries.
    - `province`: The province of the office location.

## AI Tagging Initialization
A crucial design choice in the `EskomTender` model is the handling of the `tags` attribute. In the `from_api_response` method, the `tags` field is **always initialized to an empty list ([])**.

```
# From models.py
return cls(
    # ... other fields
    tags=[],  # Initialize tags as an empty list, ready for the AI service.
    # ... other fields
)
```

This is done intentionally because the Eskom API does not provide any tags or categories. The responsibility of generating relevant `tags` is delegated to a downstream AI service that will consume the messages from the SQS queue. By initializing tags as an empty list, we provide a consistent and predictable data structure for the AI service to populate.