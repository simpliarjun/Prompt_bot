import os
import sys
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import Settings
from services.rate_limiter import compute_remaining_quota

class TestBackendUnits(unittest.TestCase):
    def test_cors_parsing_sanitizes_slashes_and_dupes(self):
        raw = "http://localhost:5173/ , http://localhost:3000 , http://localhost:5173/"
        self.assertEqual(Settings.parse_cors_origins(raw), ["http://localhost:5173", "http://localhost:3000"])

    def test_cors_parsing_handles_list_with_slashes(self):
        raw = ["http://localhost:5173/", "https://app.cgms.internal/"]
        self.assertEqual(Settings.parse_cors_origins(raw), ["http://localhost:5173", "https://app.cgms.internal"])

    def test_compute_remaining_quota(self):
        self.assertEqual(compute_remaining_quota(current=5, max_limit=20), 15)
        self.assertEqual(compute_remaining_quota(current=20, max_limit=20), 0)
        self.assertEqual(compute_remaining_quota(current=25, max_limit=20), 0)

if __name__ == "__main__":
    unittest.main()
