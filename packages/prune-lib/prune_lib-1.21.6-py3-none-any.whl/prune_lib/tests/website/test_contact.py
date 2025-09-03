import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from prune_lib.website.contact import RateLimitError, get_client_ip
from prune_lib.website.utils import check_rate_limit


def make_mock_model_with_counts(*, total_count: int, ip_count: int) -> MagicMock:
    mock_qs_total = MagicMock()
    mock_qs_total.count.return_value = total_count
    mock_qs_ip = MagicMock()
    mock_qs_ip.count.return_value = ip_count
    mock_model = MagicMock()
    mock_model.objects.filter.side_effect = [mock_qs_total, mock_qs_ip]
    return mock_model


class TestGetClientIp(unittest.TestCase):
    def setUp(self):
        request = MagicMock()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        self.request = request

    def test_with_no_x_forwarded_for(self):
        ip = get_client_ip(self.request)
        self.assertEqual(ip, "127.0.0.1")

    def test_with_x_forwarded_for(self):
        self.request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1"
        ip = get_client_ip(self.request)
        self.assertEqual(ip, "192.168.1.1")


class TestCheckRateLimit(unittest.TestCase):
    def setUp(self):
        request = MagicMock()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        self.request = request

    @patch("prune_lib.website.contact.get_client_ip")
    @patch("prune_lib.website.contact.timezone")
    def test_total_submissions_exceeded(self, mock_timezone, mock_get_client_ip):
        mock_get_client_ip.return_value = "127.0.0.1"
        mock_timezone.now.return_value = datetime(2025, 6, 5)
        mock_model = make_mock_model_with_counts(total_count=100, ip_count=4)
        with self.assertRaises(RateLimitError):
            check_rate_limit(self.request, mock_model)

    @patch("prune_lib.website.contact.get_client_ip")
    @patch("prune_lib.website.contact.timezone")
    def test_ip_limit_exceeded(self, mock_timezone, mock_get_client_ip):
        mock_get_client_ip.return_value = "192.168.0.1"
        mock_timezone.now.return_value = datetime(2025, 6, 5)
        mock_model = make_mock_model_with_counts(total_count=99, ip_count=5)
        with self.assertRaises(RateLimitError):
            check_rate_limit(self.request, mock_model)

    @patch("prune_lib.website.contact.get_client_ip")
    @patch("prune_lib.website.contact.timezone")
    def test_within_limits(self, mock_timezone, mock_get_client_ip):
        mock_get_client_ip.return_value = "10.0.0.1"
        mock_timezone.now.return_value = datetime(2025, 6, 5)
        mock_model = make_mock_model_with_counts(total_count=99, ip_count=4)
        result = check_rate_limit(self.request, mock_model)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
