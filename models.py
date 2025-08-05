from abc import ABC, abstractmethod
from datetime import datetime
import logging

"""A simple class to hold information about a supporting document."""
class SupportingDoc:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def to_dict(self):
        return {"name": self.name, "url": self.url}

class TenderBase(ABC):
    def __init__(self, title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list = None, tags: list = None):
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
        pass

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "closing_date": self.closing_date.isoformat() if self.closing_date else None,
            "supporting_docs": [doc.to_dict() for doc in self.supporting_docs],
            "tags": [tag.to_dict() for tag in self.tags]
        }

class EskomTender(TenderBase):
    def __init__(
        self,
        # Base fields
        title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list, tags: list,
        # Child fields
        tender_number: str,
        reference: str,
        audience: str,
        office_location: str,
        email: str,
        address: str,
        province: str,
    ):
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
        tender_id = response_item['TENDER_ID']

        doc_url = f"https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID={tender_id}"
        doc_list = [SupportingDoc(name="Tender Details Link", url=doc_url)]

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


        return cls(
            title=response_item.get('DESCRIPTION', '').strip(),
            description=response_item.get('SUMMARY', '').strip(),
            source="Eskom",
            published_date=pub_date,
            closing_date=close_date,
            supporting_docs=doc_list,
            tags=[],
            tender_number=tender_id,
            reference=response_item.get('REFERENCE', '').strip(),
            audience=response_item.get('Audience', '').strip(),
            office_location=response_item.get('OFFICE_LOCATION', '').strip(),
            email=response_item.get('EMAIL', '').strip(),
            address=response_item.get('ADDRESS', '').strip(),
            province=response_item.get('Province', '').strip()
        )

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "tender_number": self.tender_number,
            "reference": self.reference,
            "audience": self.audience,
            "office_location": self.office_location,
            "email": self.email,
            "address": self.address,
            "province": self.province
        })
        return data