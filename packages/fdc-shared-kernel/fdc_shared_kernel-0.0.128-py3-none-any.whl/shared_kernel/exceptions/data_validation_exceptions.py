class DataValidationException(Exception):
    """Base class for all data validation exceptions."""
    def __init__(self, message: str = "", field: str = "") -> None:
        super().__init__(message)
        self.field = field

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.args[0]} (Field: {self.field})"


class MissingField(DataValidationException):
    """Raised when a required field is missing."""
    def __init__(self, message: str = "Required field is missing", field: str = "") -> None:
        super().__init__(message=message, field=field)


class IncorrectDataType(DataValidationException):
    """Raised when the data type of a field is incorrect."""
    def __init__(self, message: str = "Incorrect data type", field: str = "", expected_type: str = "") -> None:
        super().__init__(message=f"{message} (Expected: {expected_type})", field=field)


class InvalidValue(DataValidationException):
    """Raised when the value of a field is invalid."""
    def __init__(self, message: str = "Invalid value", field: str = "", valid_values: str = "") -> None:
        super().__init__(message=f"{message} (Valid Values: {valid_values})", field=field)
