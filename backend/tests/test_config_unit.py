import unittest
import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import Settings

class TestConfigCorsParsing(unittest.TestCase):
    def test_parse_cors_origins_strips_trailing_slashes_and_duplicates(self):
        # Raw input with spaces, trailing slash, duplicate
        raw = "http://localhost:5173/ , http://localhost:3000 , http://localhost:5173/"
        parsed = Settings.parse_cors_origins(raw)
        expected = ["http://localhost:5173", "http://localhost:3000"]
        self.assertEqual(parsed, expected)

    def test_parse_cors_origins_handles_list_with_trailing_slashes(self):
        raw = ["http://localhost:5173/", "https://app.cgms.internal/"]
        parsed = Settings.parse_cors_origins(raw)
        expected = ["http://localhost:5173", "https://app.cgms.internal"]
        self.assertEqual(parsed, expected)

if __name__ == "__main__":
    unittest.main()
