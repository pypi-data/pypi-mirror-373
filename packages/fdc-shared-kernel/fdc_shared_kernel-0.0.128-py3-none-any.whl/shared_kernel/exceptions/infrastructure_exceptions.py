class InfrastructureException(Exception):
    """Base class for all infrastructure exceptions."""
    def __init__(self, message: str = "", resource: str = "") -> None:
        super().__init__(message)
        self.resource = resource

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.args[0]} (Resource: {self.resource})"


class DatabaseConnectionError(InfrastructureException):
    """Raised when there is an issue connecting to the database."""
    def __init__(self, message: str = "Failed to connect to the database", resource: str = "database") -> None:
        super().__init__(message=message, resource=resource)


class FileNotFoundError(InfrastructureException):
    """Raised when a required file or directory cannot be found."""
    def __init__(self, message: str = "File or directory not found", resource: str = "") -> None:
        super().__init__(message=message, resource=resource)


class NetworkError(InfrastructureException):
    """Raised when there is a network connectivity issue."""
    def __init__(self, message: str = "Network connectivity issue", resource: str = "network") -> None:
        super().__init__(message=message, resource=resource)