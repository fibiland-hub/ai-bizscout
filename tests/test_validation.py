import unittest
from app.validation import validate_notice, ready_for_email


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.notice = {
            "id": "official-123",
            "title": "Example",
            "agency": "Example Agency",
            "source_url": "https://example.org/notice/123",
            "start_date": "2026-11-01",
            "end_date": "2026-11-30",
            "source_verified": True,
            "dates_verified": True,
        }

    def test_valid_notice(self):
        self.assertTrue(ready_for_email(self.notice))

    def test_unverified_dates_block_email(self):
        self.notice["dates_verified"] = False
        self.assertFalse(ready_for_email(self.notice))

    def test_reversed_dates_block_email(self):
        self.notice["end_date"] = "2026-10-01"
        self.assertIn("invalid:date_range", validate_notice(self.notice))

    def test_missing_url_blocks_email(self):
        self.notice["source_url"] = ""
        self.assertFalse(ready_for_email(self.notice))


if __name__ == "__main__":
    unittest.main()
