# ==================================================================================================
#
# File: EskomLambda/models.py
#
# Description:
# This module defines the data structures (models) for representing tender information
# sourced specifically from the Eskom Tender Bulletin. It provides a structured way
# to handle, validate, and serialize tender data.
#
# The classes defined here are:
#   - SupportingDoc: A simple class to represent a downloadable document linked to a tender.
#   - TenderBase: An abstract base class defining the common interface and core attributes
#     for any tender. This promotes consistency across different tender types.
#   - EskomTender: A concrete class that inherits from TenderBase and adds fields
#     specific to the data provided by the Eskom API. It includes logic for parsing
#     the raw API response into a clean, usable object.
#
# ==================================================================================================

# Import necessary built-in modules.
# abc (Abstract Base Classes) is used to define the basic structure of a tender.
# datetime is used for handling and formatting date/time information.
# logging is used to record warnings or errors during data parsing.
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# ==================================================================================================
# Class: SupportingDoc
# Purpose: Represents a single supporting document associated with a tender.
# ==================================================================================================
class SupportingDoc:
    """
    A simple data class to hold information about a supporting document.
    This typically includes tender specifications, forms, or other relevant files.
    """
    def __init__(self, name: str, url: str):
        """
        Initializes a new instance of the SupportingDoc class.

        Args:
            name (str): The human-readable name of the document (e.g., "Tender Specifications.pdf").
            url (str): The direct URL where the document can be downloaded.
        """
        # --- Instance Attributes ---
        self.name = name  # The title or filename of the document.
        self.url = url    # The hyperlink to the document.

    def to_dict(self):
        """
        Serializes the SupportingDoc instance into a dictionary format.
        This is useful for converting the object into a JSON string for APIs or storage.

        Returns:
            dict: A dictionary containing the document's name and URL.
        """
        return {"name": self.name, "url": self.url}

# ==================================================================================================
# Class: TenderBase (Abstract Base Class)
# Purpose: Defines the fundamental structure and contract for all tender types.
# ==================================================================================================
class TenderBase(ABC):
    """
    An abstract base class that serves as a template for all specific tender models.
    It defines the common attributes and methods that every tender object must have,
    ensuring a consistent data structure regardless of the data source.
    This class cannot be instantiated directly.
    """
    def __init__(self, title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list = None, tags: list = None):
        """
        Initializes the base attributes of a tender.

        Args:
            title (str): The official title or headline of the tender.
            description (str): A detailed description of the tender's scope and requirements.
            source (str): The name of the platform where the tender was found (e.g., "Eskom").
            published_date (datetime): The date and time when the tender was officially published.
            closing_date (datetime): The date and time when submissions for the tender are due.
            supporting_docs (list, optional): A list of SupportingDoc objects. Defaults to an empty list.
            tags (list, optional): A list of keywords or categories for the tender. Defaults to an empty list.
                                   This is intentionally left empty to be populated by a downstream AI service.
        """
        # --- Instance Attributes ---
        self.title = title
        self.description = description
        self.source = source
        self.published_date = published_date
        self.closing_date = closing_date
        # If supporting_docs is not provided, initialize as an empty list to prevent errors.
        self.supporting_docs = supporting_docs if supporting_docs is not None else []
        # If tags is not provided, initialize as an empty list. This is the standard behavior
        # as the tags are expected to be added by a separate AI tagging process later.
        self.tags = tags if tags is not None else []

    @classmethod
    @abstractmethod
    def from_api_response(cls, response_item: dict):
        """
        An abstract factory method that must be implemented by all subclasses.
        Its purpose is to create a tender object from a single item (dictionary)
        from a raw API response.

        Args:
            response_item (dict): A dictionary representing one tender from the source API.

        Raises:
            NotImplementedError: If a subclass does not implement this method.
        """
        pass

    def to_dict(self):
        """
        Serializes the common tender attributes into a dictionary.
        This method is intended to be called by subclasses, which will then add their
        own specific fields to the dictionary.

        Returns:
            dict: A dictionary containing the core attributes of the tender.
        """
        return {
            "title": self.title,
            "description": self.description,
            "source": self.source,
            # Convert datetime objects to ISO 8601 format string, handling None values gracefully.
            "publishedDate": self.published_date.isoformat() if self.published_date else None,
            "closingDate": self.closing_date.isoformat() if self.closing_date else None,
            # Serialize each SupportingDoc object in the list.
            "supporting_docs": [doc.to_dict() for doc in self.supporting_docs],
            # Serialize each tag object in the list (if any).
            "tags": [tag.to_dict() for tag in self.tags]
        }

# ==================================================================================================
# Class: EskomTender
# Purpose: A concrete implementation of TenderBase for Eskom-specific tenders.
# ==================================================================================================
class EskomTender(TenderBase):
    """
    Represents a tender sourced from Eskom. It inherits all the base attributes
    from TenderBase and adds additional fields that are unique to the Eskom API data structure.
    """
    def __init__(
        self,
        # --- Base fields required by TenderBase ---
        title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list, tags: list,
        # --- Child fields specific to EskomTender ---
        tender_number: str,
        audience: str,
        office_location: str,
        email: str,
        address: str,
        province: str,
    ):
        """
        Initializes a new EskomTender instance.

        Args:
            (Inherited): title, description, source, published_date, closing_date, supporting_docs, tags.
            tender_number (str): The unique identifier for the tender (e.g., 'MWP1234PS').
            audience (str): The target audience for the tender.
            office_location (str): The Eskom office managing the tender.
            email (str): The contact email for tender inquiries.
            address (str): The physical address for tender submissions or inquiries.
            province (str): The province where the Eskom office is located.
        """
        # Call the parent class's __init__ method to set up the common fields.
        super().__init__(title, description, source, published_date, closing_date, supporting_docs, tags)
        # --- Eskom-specific Instance Attributes ---
        self.tender_number = tender_number
        self.audience = audience
        self.office_location = office_location
        self.email = email
        self.address = address
        self.province = province

    @classmethod
    def from_api_response(cls, response_item: dict):
        """
        Factory method to create an EskomTender object from a raw Eskom API response item.
        This method handles data extraction, cleaning, and validation.

        Args:
            response_item (dict): A dictionary containing a single tender's data from the Eskom API.

        Returns:
            EskomTender: An instance of the EskomTender class populated with the API data.
        """
        # Extract the tender ID, which is used for creating a document link.
        tender_id = response_item['TENDER_ID']

        # Eskom's API does not provide direct document links. We construct a link to the
        # tender details page, which acts as the primary "supporting document".
        doc_url = f"https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID={tender_id}"
        doc_list = [SupportingDoc(name="Eskom Tender Bulletin", url=doc_url)]

        # --- Date Parsing with Error Handling ---
        # Attempt to parse the published date string into a datetime object.
        try:
            pub_date = datetime.fromisoformat(response_item['PUBLISHEDDATE'])
        except (TypeError, ValueError):
            # If the date is missing, null, or in an invalid format, set it to None
            # and log a warning for monitoring purposes.
            pub_date = None
            logging.warning(f"Tender {tender_id} has invalid PUBLISHEDDATE: {response_item.get('PUBLISHEDDATE')}")
        # Attempt to parse the closing date string into a datetime object.
        try:
            close_date = datetime.fromisoformat(response_item['CLOSING_DATE'])
        except (TypeError, ValueError):
            # If the date is missing, null, or in an invalid format, set it to None
            # and log a warning.
            close_date = None
            logging.warning(f"Tender {tender_id} has invalid CLOSING_DATE: {response_item.get('CLOSING_DATE')}")

        # Create and return an instance of the EskomTender class.
        # .get() is used to safely access dictionary keys that might be missing.
        # .replace() and .strip() are used to clean string data by removing newline
        # characters and leading/trailing whitespace.
        # String methods like .title(), .upper(), and .lower() are used to standardize the text format.
        return cls(
            title=response_item.get('HEADER_DESC', '').replace('\n', ' ').replace('\r', '').strip().title(),
            description=response_item.get('SCOPE_DETAILS', '').replace('\n', ' ').replace('\r', '').strip().title(),
            source="Eskom",  # Hardcoded source for this class.
            published_date=pub_date,
            closing_date=close_date,
            supporting_docs=doc_list,
            tags=[],  # Initialize tags as an empty list, ready for the AI service.
            tender_number=response_item.get('REFERENCE', '').replace('\n', ' ').replace('\r', '').strip().upper(),
            audience=response_item.get('Audience', '').replace('\n', ' ').replace('\r', '').strip().title(),
            office_location=response_item.get('OFFICE_LOCATION', '').replace('\n', ' ').replace('\r', '').strip().title(),
            email=response_item.get('EMAIL', '').replace('\n', ' ').replace('\r', '').strip().lower(),
            address=response_item.get('ADDRESS', '').replace('\n', ' ').replace('\r', '').strip().title(),
            province=response_item.get('Province', '').replace('\n', ' ').replace('\r', '').strip().title()
        )

    def to_dict(self):
        """
        Serializes the EskomTender object to a dictionary, including both
        base and Eskom-specific fields.

        Returns:
            dict: A complete dictionary representation of the Eskom tender.
        """
        # Get the dictionary of base fields from the parent class.
        data = super().to_dict()
        # Add the Eskom-specific fields to the dictionary.
        data.update({
            "tenderNumber": self.tender_number,
            "audience": self.audience,
            "officeLocation": self.office_location,
            "email": self.email,
            "address": self.address,
            "province": self.province
        })
        # Return the final, combined dictionary.
        return data