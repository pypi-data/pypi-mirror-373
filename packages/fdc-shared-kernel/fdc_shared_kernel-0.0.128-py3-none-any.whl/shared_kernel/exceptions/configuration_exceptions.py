class ConfigurationException(Exception):
    """Base class for all configuration exceptions."""

    def __init__(self, message: str = "", config_key: str = "") -> None:
        super().__init__(message)
        self.config_key = config_key

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.args[0]} (Config Key: {self.config_key})"


class MissingConfiguration(ConfigurationException):
    """Raised when a required configuration setting is missing."""

    def __init__(
        self,
        message: str = "Required configuration setting is missing",
        config_key: str = "",
    ) -> None:
        super().__init__(message=message, config_key=config_key)


class InvalidConfiguration(ConfigurationException):
    """Raised when a configuration setting is invalid."""

    def __init__(
        self,
        message: str = "Invalid configuration setting",
        config_key: str = "",
        valid_value: str = "",
    ) -> None:
        super().__init__(
            message=f"{message} (Valid Value: {valid_value})", config_key=config_key
        )


class EnvFileNotFound(Exception):
    """Raised when a configuration setting is invalid."""

    def __init__(self, message: str = "Invalid configuration setting") -> None:
        super().__init__(f"{type(self).__name__}: {message}")
