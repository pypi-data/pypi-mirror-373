class SecurityException(Exception):
    """Base class for all security exceptions."""
    def __init__(self, message: str = "", detail: str = "") -> None:
        super().__init__(message)
        self.detail = detail

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.args[0]} (Detail: {self.detail})"


class PermissionDenied(SecurityException):
    """Raised when a user tries to access a resource without sufficient permissions."""
    def __init__(self, message: str = "Access Denied", detail: str = "") -> None:
        super().__init__(message=message, detail=detail)


class EncryptionError(SecurityException):
    """Raised when there is an issue with encryption or decryption."""
    def __init__(self, message: str = "Encryption Error", detail: str = "") -> None:
        super().__init__(message=message, detail=detail)


class CertificateVerificationError(SecurityException):
    """Raised when SSL certificate verification fails."""
    def __init__(self, message: str = "SSL Verification Failed", detail: str = "") -> None:
        super().__init__(message=message, detail=detail)
