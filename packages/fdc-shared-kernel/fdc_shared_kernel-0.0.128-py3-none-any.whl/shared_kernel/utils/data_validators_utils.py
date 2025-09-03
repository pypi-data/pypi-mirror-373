import re


class DataValidators:
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        regex = r"[^@]+@[^@]+\.[^@]+"
        return re.match(regex, email) is not None

    @staticmethod
    def validate_phone(phone_number):
        """Validate phone number format."""
        regex = r"^\d{10}$"
        return re.match(regex, phone_number) is not None
