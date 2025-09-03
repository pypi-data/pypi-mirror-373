class OperationalException(Exception):
    """Base class for all operational exceptions."""
    def __init__(self, message: str = "", cause=None) -> None:
        super().__init__(message)
        self.cause = cause

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.args[0]}"


class ServiceUnavailable(OperationalException):
    """Raised when the service is temporarily unavailable."""
    def __init__(self, message: str = "Service Unavailable", cause=None) -> None:
        super().__init__(message=message, cause=cause)


class Timeout(OperationalException):
    """Raised when an operation times out."""
    def __init__(self, message: str = "Operation Timed Out", cause=None) -> None:
        super().__init__(message=message, cause=cause)


class RateLimitExceeded(OperationalException):
    """Raised when a rate limit is exceeded."""
    def __init__(self, message: str = "Rate Limit Exceeded", cause=None) -> None:
        super().__init__(message=message, cause=cause)