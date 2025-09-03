from shared_kernel.logger import Logger
from shared_kernel.config import Config

config=Config()

class   AiAuditLog:
    """class for creating audit logs using the pre-existing logger"""

    def __new__(
        cls,
    ):
        """singleton pattern"""
        if not hasattr(cls, "_instance"):
            cls._instance = super(AiAuditLog, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
    ):
        """initialize logger for its functionality and type label"""
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.type = "ai_auditlogs"
        self.logger = Logger(config.get("APP_NAME"))

    def info(self, message, *args, **kwargs):
        """extended info function to include logs and the type of log in AiAuditLog"""
        self.logger.info(
            message=f"{message}",
            type=self.type,
            *args,
            **kwargs,
        )

    def error(self, message, *args, **kwargs):
        """extended error function to include logs and the type of log in AiAuditLog"""
        self.logger.error(
            message=f"{message}",
            type=self.type,
            *args,
            **kwargs, 
        )

    def debug(self, message, *args, **kwargs):
        """extended debug function to include logs and the type of log in AiAuditLog"""
        self.logger.debug(
            message=f"{message}",
            type=self.type,
            *args,
            **kwargs, 
        )
    def warning(self, message, *args, **kwargs):
        """extended warning function to include logs and the type of log in AiAuditLog"""
        self.logger.warning(
            message=f"{message}",
            type=self.type,
            *args,
            **kwargs, 
        )

