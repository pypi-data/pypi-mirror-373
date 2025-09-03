import unittest
from shared_kernel.utils import DataValidators


class TestDataValidators(unittest.TestCase):

    def test_validate_email(self):
        self.assertTrue(DataValidators.validate_email("test@example.com"))
        self.assertFalse(DataValidators.validate_email("not_an_email"))

    def test_validate_phone(self):
        self.assertTrue(DataValidators.validate_phone("1234567890"))
        self.assertFalse(DataValidators.validate_phone("12345"))  # Not exactly 10 digits
        self.assertFalse(DataValidators.validate_phone("123-456-7890"))  # Contains dashes


if __name__ == '__main__':
    unittest.main()
