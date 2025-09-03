import logging
import os
import json
import sys
import time
import requests
from datetime import datetime, timezone

import boto3
from shared_kernel.config import Config
from shared_kernel.utils.thread_local_storage import ThreadLocalStorage
class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter to structure log records as JSON.
    """

    def format(self, record):
        meta_data = getattr(record, 'meta_data', {})
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "filename": record.filename,
            "module": meta_data.get("module_name", record.module),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Get meta_data if present

        # Check if 'type' is in meta_data and is 'distributed_trace'
        if meta_data.get("type") == "distributed_trace":
            thread_context = ThreadLocalStorage.get_all()
            # Add each data from thread local storage
            log_record["trace_id"] = thread_context.get("trace_id")
            log_record["span_id"] = thread_context.get("span_id")
            log_record["org_id"] = thread_context.get("org_id")
            log_record["event_name"] = thread_context.get("event_name")
            log_record["event_payload"] = thread_context.get("event_payload")
            log_record["parent_span_id"] = thread_context.get("parent_span_id")
            log_record["event_meta"] = thread_context.get("event_meta")
            log_record["trigger"] = thread_context.get("trigger")
            log_record.update(meta_data)
        if hasattr(record, 'meta_data'):
            log_record.update(record.meta_data)
        if record.exc_info:
            log_record["stack_trace"] = self.formatException(record.exc_info)
            log_record["exception"] = str(record.exc_info[1])
        return json.dumps(log_record)
class Logger:
    """
    A singleton logger class that ensures only one logger instance is created.
    This logger supports both console and file logging.

    Attributes:
        _instance (Optional[Logger]): The single instance of the logger.
    """

    _instance = None

    def __new__(cls, name=None,force_prod_format=False, logger_source=None, module=None):
        """
        override __new__ to ensure singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(name=name,force_prod_format=force_prod_format, logger_source=logger_source, module=module)
        return cls._instance

    def _initialize(self, name=None, log_file: str = "fdc_app_logs.log", json_log_file: str = "fdc_app_logs.jsonl",force_prod_format=False, logger_source=None, module=None):
        # Only show warnings and above (hides INFO/DEBUG from azure libs)
        logging.getLogger("azure").setLevel(logging.WARNING)
        logging.getLogger("azure.identity").setLevel(logging.WARNING)
        logging.getLogger("azure.core").setLevel(logging.WARNING)
        self.logger = logging.getLogger(name if name else __name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.logger_source = logger_source
        self.module = module
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(filename)s - %(module)s - %(levelname)s - %(message)s"
        )
        self.log_file = log_file
        self.json_log_file = json_log_file

        # ensure handlers are configured only once
        if not self.logger.handlers:
            self.configure_logger(force_prod_format)
        if self.logger_source == "glue":
            self._init_cloudwatch_logger()

    def _init_cloudwatch_logger(self):
        self.cloudwatch_client = boto3.client("logs", region_name="us-east-1")
        self.cloudwatch_log_group = "/aws-glue/jobs/custom"
        self.cloudwatch_log_stream = f"glue_job_{int(time.time())}"
        self.sequence_token = None

        # Ensure the log group exists
        try:
            self.cloudwatch_client.create_log_group(logGroupName=self.cloudwatch_log_group)
        except self.cloudwatch_client.exceptions.ResourceAlreadyExistsException:
            pass

        # Create a new log stream
        try:
            self.cloudwatch_client.create_log_stream(
                logGroupName=self.cloudwatch_log_group,
                logStreamName=self.cloudwatch_log_stream
            )
        except self.cloudwatch_client.exceptions.ResourceAlreadyExistsException:
            pass
    def configure_logger(self,force_prod_format):
        """
        Configures logger with stream and file handlers.
        """
        self.add_stream_handler(force_prod_format)
        self.add_file_handler(log_file=self.log_file)
        self.add_json_file_handler(log_file=self.json_log_file)

    def add_stream_handler(self,force_prod_format):
        """
        Adds a stream handler to the logger.
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.logger.level)

        mode = "PROD" if force_prod_format else Config().get("MODE")
        stream_handler.setFormatter(JSONFormatter() if mode == "PROD" else self.formatter)
        self.logger.addHandler(stream_handler)

    def add_file_handler(self, log_file, log_directory="./logs"):
        """
        Adds a file handler to the logger.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        file_handler = logging.FileHandler(os.path.join(log_directory, log_file))
        file_handler.setLevel(self.logger.level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def add_json_file_handler(self, log_file, log_directory="./logs"):
        """
        Adds a JSON file handler to the logger.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        json_file_handler = logging.FileHandler(os.path.join(log_directory, log_file))
        json_file_handler.setLevel(self.logger.level)
        json_file_handler.setFormatter(JSONFormatter())  # Using the custom JSON formatter
        self.logger.addHandler(json_file_handler)

    def send_to_cloudwatch(self, formatted_message: str):
        timestamp = int(time.time() * 1000)
        kwargs = {
            "logGroupName": self.cloudwatch_log_group,
            "logStreamName": self.cloudwatch_log_stream,
            "logEvents": [{
                "timestamp": timestamp,
                "message": formatted_message
            }]
        }
        if self.sequence_token:
            kwargs["sequenceToken"] = self.sequence_token

        try:
            response = self.cloudwatch_client.put_log_events(**kwargs)
            self.sequence_token = response['nextSequenceToken']
        except self.cloudwatch_client.exceptions.InvalidSequenceTokenException as e:
            correct_token = e.response['Error']['Message'].split()[-1]
            self.sequence_token = correct_token
            kwargs["sequenceToken"] = self.sequence_token
            response = self.cloudwatch_client.put_log_events(**kwargs)
            self.sequence_token = response['nextSequenceToken']

    def _log_and_send(self, level, message, *args, exc_info=None, **kwargs):
        meta_data = {"meta_data": kwargs}
        if level == logging.ERROR:
            exc_info  = sys.exc_info()
        self.logger.log(level, message, *args, extra=meta_data, stacklevel=2, exc_info=exc_info)

        if self.logger_source == "glue":
            formatter = JSONFormatter()
            record = self.logger.makeRecord(
                name=self.logger.name,
                level=level,
                fn="",
                lno=0,
                msg=message,
                args=args,
                exc_info=exc_info,
                extra=meta_data
            )
            record.module = self.module
            formatted_message = formatter.format(record)
            self.send_to_cloudwatch(formatted_message)

    def info(self, message, *args, **kwargs):
        self._log_and_send(logging.INFO, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log_and_send(logging.ERROR, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self._log_and_send(logging.DEBUG, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log_and_send(logging.WARNING, message, *args, **kwargs)
    def alert(self, message, severity="critical", description=None, alertname="ApplicationError", ServiceName=None, group="application"):
        """
        Sends a Grafana OnCall-compatible alert using a webhook.

        Args:
            message (str): Title of the alert.
            severity (str): 'critical', 'warning', etc.
            description (str): Optional detailed description.
            alertname (str): Alert name identifier.
            group (str): Group name (e.g., 'production', 'application').
            job (str): Job name (e.g., 'api-server').
        """
        self._log_and_send(logging.CRITICAL, message, severity=severity, description=description)

        try:
            webhook_url = Config().get("ALERT_WEBHOOK_URL")
            now = datetime.now(timezone.utc).isoformat()

            alert_payload = {
                "alerts": [
                    {
                        "status": "firing",
                        "labels": {
                            "alertname": alertname,
                            "severity": severity,
                            "Service": ServiceName,
                            "group": group
                        },
                        "annotations": {
                            "title": message,
                            "description": description or message
                        },
                        "startsAt": now,
                        "endsAt": "0001-01-01T00:00:00Z",
                        "generatorURL": "",
                        "fingerprint": ""
                    }
                ],
                "status": "firing",
                "version": "4",
                "receiver": "combo",
                "groupLabels": {
                    "alertname": alertname
                },
                "commonLabels": {
                    "alertname": alertname,
                    "severity": severity,
                    "Description": description or message,
                    "Service": ServiceName,
                },
                "commonAnnotations": {},
                "externalURL": "",
                "groupKey": "{}:{alertname=\"%s\"}" % alertname,
                "numFiring": 1,
                "numResolved": 0,
                "truncatedAlerts": 0
            }

            response = requests.post(webhook_url, json=alert_payload, timeout=5)
            response.raise_for_status()

        except Exception as e:
            self.logger.error("Failed to send alert: %s", str(e), exc_info=True)
