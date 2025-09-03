from datetime import datetime
from shared_kernel.utils import DateFormatUtils
import unittest


class TestDateFormatUtils(unittest.TestCase):

    def test_format_date(self):
        now = datetime.now()
        formatted_now = DateFormatUtils.format_date(now)
        self.assertEqual(formatted_now, now.strftime("%Y-%m-%d"))

    def test_parse_date(self):
        date_str = "2024-07-17"
        parsed_date = DateFormatUtils.parse_date(date_str)
        self.assertEqual(parsed_date.strftime("%Y-%m-%d"), date_str)


if __name__ == '__main__':
    unittest.main()
