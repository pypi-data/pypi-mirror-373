import http


class HTTPException(Exception):
    """Base class for all HTTP exceptions."""

    def __init__(self, message: str = "", code: int = None) -> None:
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        return f"{super().__str__()}"


class BadRequest(HTTPException):
    """Raised for HTTP 400 Bad Request errors."""
    code = http.HTTPStatus.BAD_REQUEST.value

    def __init__(self, message: str = "Bad Request", code: int = 400) -> None:
        super().__init__(message=message, code=code or self.code)


class Unauthorized(HTTPException):
    """Raised for HTTP 401 Unauthorized errors."""
    code = http.HTTPStatus.UNAUTHORIZED.value

    def __init__(self, message: str = "Unauthorized", code: int = 401) -> None:
        super().__init__(message=message, code=code or self.code)


class Forbidden(HTTPException):
    """Raised for HTTP 403 Forbidden errors."""
    code = http.HTTPStatus.FORBIDDEN.value

    def __init__(self, message: str = "Forbidden", code: int = 403) -> None:
        super().__init__(message=message, code=code or self.code)


class NotFound(HTTPException):
    """Raised for HTTP 404 Not Found errors."""
    code = http.HTTPStatus.NOT_FOUND.value

    def __init__(self, message: str = "Not Found", code: int = 404) -> None:
        super().__init__(message=message, code=code or self.code)


class Conflict(HTTPException):
    """Raised for HTTP 409 Conflict errors."""
    code = http.HTTPStatus.CONFLICT.value

    def __init__(self, message: str = "Conflict", code: int = 409) -> None:
        super().__init__(message=message, code=code or self.code)


class InternalServerError(HTTPException):
    """Raised for HTTP 500 Internal Server Error."""
    code = http.HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message: str = "Internal Server Error", code: int = 500) -> None:
        super().__init__(message=message, code=code or self.code)
