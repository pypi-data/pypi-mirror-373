import unittest
from shared_kernel.utils import StringUtils


class TestStringUtils(unittest.TestCase):

    def test_no_truncation_needed(self):
        self.assertEqual(StringUtils.truncate_string("Hello, world!", 20), "Hello, world!")

    def test_truncation_with_default_suffix(self):
        self.assertEqual(StringUtils.truncate_string("Hello, world!", 8), "Hello...")

    def test_truncation_with_custom_suffix(self):
        self.assertEqual(StringUtils.truncate_string("Hello, world!", 10, suffix='***'), "Hello, ***")

    def test_empty_string(self):
        self.assertEqual(StringUtils.truncate_string("", 5), "")

    def test_suffix_longer_than_max_length(self):
        self.assertEqual(StringUtils.truncate_string("Hello", 3, suffix='***'), '***')

    def test_remove_html_tags(self):
        self.assertEqual(StringUtils.remove_html_tags("<p>Hello, <strong>world</strong>!</p>"),
                         "Hello, world!")


if __name__ == '__main__':
    unittest.main()
