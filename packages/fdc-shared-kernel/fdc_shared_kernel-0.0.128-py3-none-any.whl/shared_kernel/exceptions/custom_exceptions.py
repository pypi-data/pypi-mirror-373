class BaseCustomException(Exception):
    """Base class for all custom logic exceptions."""
    def __init__(self, message: str = "", details: str = "") -> None:
        super().__init__(message)
        self.details = details

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.args[0]} (Details: {self.details})"


class UnsupportedProfiling(BaseCustomException):
    """Raised when an unsupported data profiling method is requested."""
    def __init__(self, message: str = "The profiling method is not supported.", details: str = "") -> None:
        super().__init__(message=message, details=details)


class StatusTrackerException(BaseCustomException):
    """Raised when an error occurs during status tracker operations."""
    def __init__(self, message: str = "An error occurred during status tracking.") -> None:
        super().__init__(message=message)