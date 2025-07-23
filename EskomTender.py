from TenderBase import TenderBase
from datetime import datetime

class EskomTender(TenderBase):
    """Deserializes tender data from the Eskom Tender Bulletin."""
    def __init__(
        self,
        # Base fields
        tender_number: str, title: str, description: str, source_name: str,
        source_url: str, closing_date: datetime, published_date: datetime,
        # Child fields
        reference: str, office_location: str, email: str, province: str, e_tendering: bool
    ):
        super().__init__(tender_number, title, description, source_name, source_url, closing_date, published_date)
        self.reference = reference
        self.office_location = office_location
        self.email = email
        self.province = province
        self.e_tendering = e_tendering

    @classmethod
    def from_api_response(cls, response_item: dict):
        tender_id = response_item['TENDER_ID']
        return cls(
            tender_number=response_item.get('REFERENCE', f"ESK{tender_id}"),
            title=response_item.get('HEADER_DESC', 'No Title Provided').strip(),
            description=response_item.get('SUMMARY', '').strip(),
            source_name="Eskom",
            source_url=f"https://tenderbulletin.eskom.co.za/webapi/api/Lookup/GetTender?TENDER_ID={tender_id}",
            closing_date=datetime.fromisoformat(response_item['CLOSING_DATE']),
            published_date=datetime.fromisoformat(response_item['PUBLISHEDDATE']),
            reference=response_item.get('REFERENCE', 'N/A'),
            office_location=response_item.get('OFFICE_LOCATION', 'N/A'),
            email=response_item.get('EMAIL') or 'not-provided@eskom.co.za', # Ensure no nulls
            province=response_item.get('Province', 'National'),
            e_tendering=response_item.get('E_TENDERING', False)
        )

    # --- ADD THIS METHOD ---
    def to_dict(self):
        """Overrides base method to include child-specific fields."""
        data = super().to_dict()
        data.update({
            "reference": self.reference,
            "office_location": self.office_location,
            "email": self.email,
            "province": self.province,
            "e_tendering": self.e_tendering
        })
        return data