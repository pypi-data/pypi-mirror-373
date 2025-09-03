import unittest

from prune_lib.commons.strings import is_valid_regex


class TestIsValidRegex(unittest.TestCase):
    def test_with_invalid_regex(self):
        result = is_valid_regex(r"([A-Z]+")
        self.assertFalse(result)

    def test_with_valid_regex(self):
        result = is_valid_regex(r"^[\d\+\- \(\)]{6, 20}$")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
