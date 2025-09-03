import unittest
from unittest.mock import MagicMock

from prune_lib.commons.parse import get_data_from_request


def make_mock_with_dict(*, dict: dict) -> MagicMock:
    mock = MagicMock()
    mock.dict.return_value = dict
    return mock


class TestGetDataFromRequest(unittest.TestCase):
    def setUp(self):
        request = MagicMock()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        self.request = request

    def test_get_method(self):
        self.request.method = "GET"
        self.request.GET = make_mock_with_dict(dict={"name": "Jean", "age": "30"})
        data = get_data_from_request(self.request)
        self.assertEqual(data, {"name": "Jean", "age": "30"})

    def test_post_json(self):
        self.request.method = "POST"
        self.request.content_type = "application/json"
        self.request.body = b'{"email": "test@example.com", "subscribed": true}'
        data = get_data_from_request(self.request)
        self.assertEqual(data, {"email": "test@example.com", "subscribed": True})

    def test_post_form_data(self):
        self.request.method = "POST"
        self.request.content_type = "application/x-www-form-urlencoded"
        self.request.POST = make_mock_with_dict(dict={"city": "Paris", "zip": "75000"})
        self.request.FILES = make_mock_with_dict(dict={})
        data = get_data_from_request(self.request)
        self.assertEqual(data, {"city": "Paris", "zip": "75000"})

    def test_post_multipart_with_files(self):
        self.request.method = "POST"
        self.request.content_type = "multipart/form-data"
        self.request.POST = make_mock_with_dict(dict={"field": "value"})
        mock_file = MagicMock()
        self.request.FILES = make_mock_with_dict(dict={"file": mock_file})
        data = get_data_from_request(self.request)
        self.assertEqual(data, {"field": "value", "file": mock_file})

    def test_unsupported_method(self):
        self.request.method = "PATCH"
        with self.assertRaises(NotImplementedError):
            get_data_from_request(self.request)

    def test_unsupported_content_type(self):
        self.request.method = "POST"
        self.request.content_type = "text/plain"
        with self.assertRaises(NotImplementedError):
            get_data_from_request(self.request)


if __name__ == "__main__":
    unittest.main()
