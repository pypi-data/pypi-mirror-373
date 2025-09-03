import unittest
from datetime import datetime

from prune_lib.commons.dates import add_months, get_datetime_of_first_day_of_month


class TestAddMonths(unittest.TestCase):
    def test_add_months(self):
        dt = datetime.now()
        number_of_months_to_increment = 7
        new_dt = add_months(dt, months=number_of_months_to_increment)
        delta = 12 - dt.month
        expected_month = number_of_months_to_increment - delta
        self.assertEqual(new_dt.month, expected_month)


class TestGetDatetimeOfFirstDayOfMonth(unittest.TestCase):
    def test_get_datetime_of_first_day_of_month(self):
        dt = datetime.now()
        datetime_of_first_day_of_month = get_datetime_of_first_day_of_month()
        self.assertEqual(datetime_of_first_day_of_month.month, dt.month)
        self.assertEqual(datetime_of_first_day_of_month.day, 1)


if __name__ == "__main__":
    unittest.main()
