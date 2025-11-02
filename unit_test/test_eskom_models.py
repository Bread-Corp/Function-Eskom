import unittest
from datetime import datetime
from models import EskomTender, SupportingDoc

class TestEskomModels(unittest.TestCase):

    def test_from_api_response_valid(self):
        sample = {
            "TENDER_ID": "123",
            "HEADER_DESC": "Upgrade of Substation",
            "SCOPE_DETAILS": "Full electrical overhaul",
            "PUBLISHEDDATE": "2025-10-01T09:00:00",
            "CLOSING_DATE": "2025-10-31T16:00:00",
            "REFERENCE": "MWP1234PS",
            "Audience": "Suppliers",
            "OFFICE_LOCATION": "Megawatt Park",
            "EMAIL": "tenders@eskom.co.za",
            "ADDRESS": "1 Maxwell Drive, Sunninghill",
            "Province": "Gauteng"
        }

        tender = EskomTender.from_api_response(sample)
        self.assertIsNotNone(tender)
        self.assertEqual(tender.tender_number, "MWP1234PS")
        self.assertEqual(tender.office_location, "Megawatt Park")
        self.assertEqual(tender.email, "tenders@eskom.co.za")
        self.assertEqual(len(tender.supporting_docs), 1)

    def test_from_api_response_invalid_dates(self):
        sample = {
            "TENDER_ID": "123",
            "HEADER_DESC": "Upgrade of Substation",
            "SCOPE_DETAILS": "Full electrical overhaul",
            "PUBLISHEDDATE": "invalid-date",
            "CLOSING_DATE": None,
            "REFERENCE": "MWP1234PS",
            "Audience": "Suppliers",
            "OFFICE_LOCATION": "Megawatt Park",
            "EMAIL": "tenders@eskom.co.za",
            "ADDRESS": "1 Maxwell Drive, Sunninghill",
            "Province": "Gauteng"
        }

        tender = EskomTender.from_api_response(sample)
        self.assertIsNone(tender.published_date)
        self.assertIsNone(tender.closing_date)

    def test_to_dict_structure(self):
        tender = EskomTender(
            title="Substation Upgrade",
            description="Fix transformers",
            source="Eskom",
            published_date=datetime(2025, 10, 1, 9, 0),
            closing_date=datetime(2025, 10, 31, 16, 0),
            supporting_docs=[SupportingDoc("Doc", "https://example.com")],
            tags=[],
            tender_number="MWP1234PS",
            audience="Suppliers",
            office_location="Megawatt Park",
            email="tenders@eskom.co.za",
            address="1 Maxwell Drive",
            province="Gauteng"
        )
        data = tender.to_dict()
        self.assertEqual(data["title"], "Substation Upgrade")
        self.assertEqual(data["supporting_docs"][0]["url"], "https://example.com")
        self.assertEqual(data["email"], "tenders@eskom.co.za")

if __name__ == '__main__':
    unittest.main()
