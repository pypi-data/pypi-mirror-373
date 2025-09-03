import re


class StringUtils:
    @staticmethod
    def truncate_string(s, max_length, suffix='...'):
        """
        Truncate a string to a specified length and add a suffix if truncated.

        Parameters:
        s (str): The string to truncate.
        max_length (int): The maximum length of the truncated string including the suffix.
        suffix (str): The suffix to add if the string is truncated. Default is '...'.

        Returns:
        str: The truncated string.
        """
        if len(s) <= max_length:
            return s
        if len(suffix) >= max_length:
            return suffix[:max_length]
        return s[:max_length - len(suffix)] + suffix

    @staticmethod
    def remove_html_tags(text):
        """Remove HTML tags from text."""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
