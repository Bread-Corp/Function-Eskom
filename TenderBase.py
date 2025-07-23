from abc import ABC, abstractmethod
from datetime import datetime

class TenderBase(ABC):
    """
    An abstract base class representing the common, non-nullable fields 
    found across all tender sources.
    """
    def __init__(
        self,
        tender_number: str,
        title: str,
        description: str,
        source_name: str,
        source_url: str,
        closing_date: datetime,
        published_date: datetime,
    ):
        self.tender_number = tender_number
        self.title = title
        self.description = description
        self.source_name = source_name
        self.source_url = source_url
        self.closing_date = closing_date
        self.published_date = published_date

    @classmethod
    @abstractmethod
    def from_api_response(cls, response_item: dict):
        """Each child class must implement this to parse its specific API response."""
        pass

    def to_dict(self):
        """A helper method to convert the object to a dictionary."""
        return {
            "tender_number": self.tender_number,
            "title": self.title,
            "description": self.description,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "closing_date": self.closing_date.isoformat(),
            "published_date": self.published_date.isoformat(),
        }