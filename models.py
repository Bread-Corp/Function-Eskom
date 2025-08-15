"""
This module defines the data models for representing tender information.

It includes:
- SupportingDoc: A simple class to hold details of a supporting document.
- TenderBase: An abstract base class that defines the common structure and
  interface for any tender, ensuring that subclasses implement key methods.
- EskomTender: A concrete implementation of TenderBase, specifically for
  handling and validating tender data from the Eskom API.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging

class SupportingDoc:
    """
    Represents a single supporting document associated with a tender.
    """
    def __init__(self, name: str, url: str):
        """
        Initializes a SupportingDoc instance.

        Args:
            name (str): The display name or title of the document.
            url (str): The direct URL to access the document.
        """
        self.name = name
        self.url = url

    def to_dict(self):
        """
        Serializes the SupportingDoc object to a dictionary.

        Returns:
            dict: A dictionary representation of the document.
        """
        return {"name": self.name, "url": self.url}

class TenderBase(ABC):
    """
    An abstract base class for a tender.

    This class defines the core attributes and methods that any tender object
    should have. It cannot be instantiated directly and requires subclasses
    to implement the `from_api_response` method.
    """
    def __init__(self, title: str, description: str, source: str,
                 published_date: datetime, closing_date: datetime,
                 supporting_docs: list = None, tags: list = None):
        """
        Initializes the base attributes of a tender.

        Args:
            title (str): The title of the tender.
            description (str): A detailed description of the tender.
            source (str): The originating source of the tender (e.g., "Eskom").
            published_date (datetime): The date and time when the tender was published.
            closing_date (datetime): The deadline for submissions.
            supporting_docs (list, optional): A list of SupportingDoc objects. Defaults to None.
            tags (list, optional): A list of relevant tags or keywords. Defaults to None.
        """
        self.title = title
        self.description = description
        self.source = source
        self.published_date = published_date
        self.closing_date = closing_date
        self.supporting_docs = supporting_docs if supporting_docs is not None else []
        self.tags = tags if tags is not None else []

    @classmethod
    @abstractmethod
    def from_api_response(cls, response_item: dict):
        """
        An abstract class method to create a tender object from a raw API response.

        Subclasses must implement this method to handle the specific structure
        of their source API data.

        Args:
            response_item (dict): A single item (dictionary) from an API response.

        Raises:
            NotImplementedError: If a subclass does not implement this method.
        """
        pass

    def to_dict(self):
        """
        Serializes the base tender data to a dictionary.

        Converts datetime objects to ISO 8601 string format for JSON compatibility.

        Returns:
            dict: A dictionary representation of the tender's base fields.
        """
        return {
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "publishedDate": self.published_date.isoformat() if self.published_date else None,
            "closingDate": self.closing_date.isoformat() if self.closing_date else None,
            "supporting_docs": [doc.to_dict() for doc in self.supporting_docs],
            "tags": self.tags # Assuming tags are simple strings or already dicts
        }

class EskomTender(TenderBase):
    """
    Represents a tender specifically from the Eskom Tender Bulletin.

    This class extends TenderBase and includes additional fields specific to
    Eskom's data structure. It provides a concrete implementation of the
    `from_api_response` factory method to parse and validate Eskom API data.
    """
    def __init__(
        self,
        # Fields from TenderBase
        title: str, description: str, source: str, published_date: datetime,
        closing_date: datetime, supporting_docs: list, tags: list,
        # Fields specific to EskomTender
        tender_number: str,
        reference: str,
        audience: str,
        office_location: str,
        email: str,
        address: str,
        province: str,
    ):
        """
        Initializes an EskomTender instance.

        Args:
            (See TenderBase for base field descriptions)
            tender_number (str): The unique identifier for the tender (TENDER_ID).
            reference (str): The reference number for the tender.
            audience (str): The target audience for the tender.
            office_location (str): The location of the relevant Eskom office.
            email (str): Contact email for inquiries.
            address (str): Physical or postal address for the tender.
            province (str): The province where the tender is located.
        """
        super().__init__(title, description, source, published_date, closing_date, supporting_docs, tags)
        self.tender_number = tender_number
        self.reference = reference
        self.audience = audience
        self.office_location = office_location
        self.email = email
        self.address = address
        self.province = province

    @classmethod
    def from_api_response(cls, response_item: dict):
        """
        Factory method to create an EskomTender object from a raw Eskom API dictionary.

        This method handles data extraction, cleaning (e.g., stripping whitespace),
        and type conversion (e.g., parsing dates). It includes robust error handling
        for date parsing and safely accesses dictionary keys using .get().

        Args:
            response_item (dict): A dictionary representing a single tender from the Eskom API response.

        Returns:
            EskomTender: An initialized instance of the EskomTender class.

        Raises:
            KeyError: If the required 'TENDER_ID' key is missing in the response_item.
        """
        # A KeyError will be raised if 'TENDER_ID' is missing, which is caught in the lambda handler.
        tender_id = response_item['TENDER_ID']

        # Create a supporting document link back to the Eskom bulletin.
        doc_url = f"https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID={tender_id}"
        doc_list = [SupportingDoc(name="Eskom Tender Bulletin", url=doc_url)]

        # Safely parse date strings into datetime objects. If parsing fails,
        # set to None and log a warning.
        try:
            pub_date = datetime.fromisoformat(response_item['PUBLISHEDDATE'])
        except (TypeError, ValueError):
            pub_date = None
            logging.warning(f"Tender {tender_id} has invalid PUBLISHEDDATE: {response_item.get('PUBLISHEDDATE')}")
        try:
            close_date = datetime.fromisoformat(response_item['CLOSING_DATE'])
        except (TypeError, ValueError):
            close_date = None
            logging.warning(f"Tender {tender_id} has invalid CLOSING_DATE: {response_item.get('CLOSING_DATE')}")

        # Use .get(key, default_value) for safe access to optional fields.
        # Clean string fields by removing newline characters and stripping whitespace.
        return cls(
            title=response_item.get('HEADER_DESC', '').replace('\n', ' ').replace('\r', '').strip(),
            description=response_item.get('SCOPE_DETAILS', '').replace('\n', ' ').replace('\r', '').strip(),
            source="Eskom",
            published_date=pub_date,
            closing_date=close_date,
            supporting_docs=doc_list,
            tags=[],  # Eskom API does not provide tags, so initialize as empty.
            tender_number=tender_id,
            reference=response_item.get('REFERENCE', '').replace('\n', ' ').replace('\r', '').strip(),
            audience=response_item.get('Audience', '').replace('\n', ' ').replace('\r', '').strip(),
            office_location=response_item.get('OFFICE_LOCATION', '').replace('\n', ' ').replace('\r', '').strip(),
            email=response_item.get('EMAIL', '').replace('\n', ' ').replace('\r', '').strip(),
            address=response_item.get('ADDRESS', '').replace('\n', ' ').replace('\r', '').strip(),
            province=response_item.get('Province', '').replace('\n', ' ').replace('\r', '').strip()
        )

    def to_dict(self):
        """
        Serializes the EskomTender object to a dictionary.

        This method first calls the parent `to_dict` method to get the base
        fields, then updates the dictionary with the fields specific to EskomTender.

        Returns:
            dict: A complete dictionary representation of the Eskom tender.
        """
        data = super().to_dict()
        data.update({
            "tenderNumber": self.tender_number,
            "reference": self.reference,
            "audience": self.audience,
            "officeLocation": self.office_location,
            "email": self.email,
            "address": self.address,
            "province": self.province
        })
        return data