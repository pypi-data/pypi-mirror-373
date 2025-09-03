import unittest

from prune_lib.logic.cleaned_data import clean_phone


class TestCleanedData(unittest.TestCase):
    def test_invalid_phone_number(self):
        with self.assertRaises(ValueError):
            clean_phone("1234")
        with self.assertRaises(ValueError):
            clean_phone("fake-phone-number")

    def test_valid_phone_number(self):
        cleaned_phone_number = clean_phone("0604529465")
        self.assertIsNotNone(cleaned_phone_number)
        cleaned_phone_number = clean_phone("06 52 45 65 88")
        self.assertIsNotNone(cleaned_phone_number)
        cleaned_phone_number = clean_phone("+33 6 52 12 45 66")
        self.assertIsNotNone(cleaned_phone_number)


if __name__ == "__main__":
    unittest.main()
