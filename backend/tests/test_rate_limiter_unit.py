import unittest
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.rate_limiter import compute_remaining_quota

class TestRateLimiterQuota(unittest.TestCase):
    def test_compute_remaining_quota_normal(self):
        self.assertEqual(compute_remaining_quota(current=5, max_limit=20), 15)

    def test_compute_remaining_quota_at_limit(self):
        self.assertEqual(compute_remaining_quota(current=20, max_limit=20), 0)

    def test_compute_remaining_quota_over_limit_never_negative(self):
        self.assertEqual(compute_remaining_quota(current=25, max_limit=20), 0)

if __name__ == "__main__":
    unittest.main()
