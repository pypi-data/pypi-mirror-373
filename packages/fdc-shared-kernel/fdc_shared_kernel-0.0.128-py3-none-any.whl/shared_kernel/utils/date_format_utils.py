from datetime import datetime


class DateFormatUtils:
    @staticmethod
    def format_date(date_obj, format_str="%Y-%m-%d"):
        """Format a date object according to the given format string."""
        return date_obj.strftime(format_str)

    @staticmethod
    def parse_date(date_str, format_str="%Y-%m-%d"):
        """Parse a date string into a date object."""
        return datetime.strptime(date_str, format_str)
