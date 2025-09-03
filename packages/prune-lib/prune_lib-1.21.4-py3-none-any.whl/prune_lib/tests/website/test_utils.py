import unittest
from unittest.mock import MagicMock, patch

from prune_lib.website.contact import RateLimitError
from prune_lib.website.utils import verify_form_with_captcha_and_rate_limit


class TestVerifyFormWithCaptchaAndRateLimit(unittest.TestCase):
    def setUp(self):
        request = MagicMock()
        self.mock_model = MagicMock()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        self.request = request

    @patch("prune_lib.website.utils.verify_captcha")
    def test_verify_captcha_return_false(self, mock_verify_captcha):
        mock_verify_captcha.return_value = False
        result = verify_form_with_captcha_and_rate_limit(self.request, self.mock_model)
        self.assertFalse(result)

    @patch("prune_lib.website.utils.verify_captcha")
    @patch("prune_lib.website.utils.check_rate_limit")
    def test_verify_captcha_return_true_check_rate_limit_raise_rate_limit_error(
        self, mock_check_rate_limit, mock_verify_captcha
    ):
        mock_verify_captcha.return_value = True
        mock_check_rate_limit.side_effect = RateLimitError
        result = verify_form_with_captcha_and_rate_limit(self.request, self.mock_model)
        self.assertFalse(result)

    @patch("prune_lib.website.utils.verify_captcha")
    @patch("prune_lib.website.utils.check_rate_limit")
    def test_verify_captcha_return_true_check_rate_limit_return_true(
        self, mock_check_rate_limit, mock_verify_captcha
    ):
        mock_verify_captcha.return_value = True
        mock_check_rate_limit.return_value = None
        result = verify_form_with_captcha_and_rate_limit(self.request, self.mock_model)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
