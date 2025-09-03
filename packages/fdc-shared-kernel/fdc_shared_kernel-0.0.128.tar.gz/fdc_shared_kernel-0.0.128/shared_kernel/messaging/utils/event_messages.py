from datetime import datetime, timezone
import json
from typing import Any, Dict
import uuid
from nats.aio.msg import Msg


class EventMeta:
    """Class representing metadata for an event message.
    
    Attributes:
        trace_id (str): Unique identifier for tracing a request across services.
        span_id (str): Unique identifier for this specific operation within the trace.
        job_id (str): Identifier for the job associated with this event.
    """
    ALLOWED_TRIGGER_BY_VALUES = {"SCHEDULER", "PROVISION", "MANUAL", "EVENT"}

    def __init__(self, meta_data: Dict):
        self.trace_id: str = meta_data.get("trace_id")
        self.job_id: str = meta_data.get("job_id")
        self.trigger = meta_data.get("trigger")
        self.org_id = meta_data.get("org_id")
        # entity_id is an optional field as some events may not be associated with an entity
        self.entity_id = meta_data.get("entity_id", None)
        # keep the scheduler id for azure queue
        self.scheduler_id= None

        # parent_span_id is an optional field as some events may not be associated with an entity
        self.parent_span_id = meta_data.get("parent_span_id", None)

        # generate a new span_id for each event if not present already
        self.span_id: str = meta_data.get("span_id", str(uuid.uuid4()))

        if self.trigger and self.trigger not in self.ALLOWED_TRIGGER_BY_VALUES:
            raise ValueError(f"Invalid trigger value: {self.trigger}. Must be one of {self.ALLOWED_TRIGGER_BY_VALUES}.")

        # time taken for the entire execution of the event
        self.start_time_str: str = None
        self.start_time_dt: datetime = None
        self.end_time_str: str = None
        self.end_time_dt: datetime = None
        self.time_taken: int = None

        # failure reason if any
        self.failure_reason: str = None

        self.additional_fields: Dict[str, Any] = {k: v for k, v in meta_data.items() if k not in {"trace_id", "job_id", "span_id"}}

    def start_event_timer(self):
        """Sets the start time of the event."""
        self.start_time_dt = datetime.now(timezone.utc)
        self.start_time_str = self.start_time_dt.isoformat()

    def end_event_timer(self, unit: str = "seconds"):
        """Sets the end time of the event and calculates time taken in the specified unit.
        
        Args:
            unit (str): The unit to display time taken. Options: "seconds", "minutes", "hours".
                        Defaults to "seconds".
        """
        if self.start_time_str is None:
            raise ValueError("start_time must be set before end_time.")
        
        self.end_time_dt = datetime.now(timezone.utc)
        self.end_time_str = self.end_time_dt.isoformat()
        
        # calculate the difference in seconds
        duration_seconds = (self.end_time_dt - self.start_time_dt).total_seconds()

        # convert to the specified unit
        if unit == "minutes":
            self.time_taken = duration_seconds / 60
        elif unit == "hours":
            self.time_taken = duration_seconds / 3600
        else:  # default to seconds
            self.time_taken = duration_seconds

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the event metadata."""
        base_dict = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "job_id": self.job_id,
            "start_time": self.start_time_str or "",
            "end_time": self.end_time_str or "",
            "time_taken": self.time_taken if self.time_taken else "",
        }
        # merge core fields with additional fields
        return {**base_dict, **self.additional_fields}


class PublishEventMessage:
    """Base class for creating standardized event messages to be published to message brokers.
    
    This class provides a consistent format for event messages with support for distributed
    tracing through trace_id and span_id. If trace_id or span_id are not provided in the
    input dictionary, they will be automatically generated using UUID4.
    
    Attributes:
        event_dict (Dict[str, Any]): Dictionary containing complete event data including:
            - event_name: Name of the event being published
            - payload: Event payload containing event-specific data
            - event_meta: Dictionary containing trace_id and span_id
    """

    def __init__(self, event_dict: Dict[str, Any]):
        """Initialize the message with a complete event dictionary.
        
        Args:
            event_dict: Dictionary containing event data in the format:
                {
                    "event_name": str,
                    "event_payload": dict,
                    "event_meta": {
                        "trace_id": str,
                        "span_id": str
                    }
                }
        """
        self.event_dict = event_dict
        self._validate_and_set_metadata()

    def _validate_and_set_metadata(self):
        """Validates and sets metadata in the event dictionary.
        
        If event_meta section doesn't exist, creates it.
        If span_id don't exist, generates them using UUID4.
        """
        # ensure event_meta dictionary exists
        if "event_meta" not in self.event_dict or not self.event_dict["event_meta"]["trace_id"]:
            raise Exception("Message metadata or trace_id not found.")

        # always generate a new job id and span id
        self.event_dict["event_meta"]["job_id"] = str(uuid.uuid4())
        self.event_dict["event_meta"]["span_id"] = str(uuid.uuid4())

    def to_dict(self) -> dict:
        """Convert the event to a dictionary format"""
        return self.event_dict

    def to_json(self) -> str:
        """Convert the event to a JSON string"""
        return json.dumps(self.event_dict)


class EventMessage:
    """Base class for handling received event messages from message brokers.
    
    This class provides a standardized way to parse and access event message data
    regardless of the message broker source.
    
    Attributes:
        raw_message (dict): The original raw message received.
        event_name (str): Name of the received event.
        event_payload (dict): Event payload containing event-specific data.
        event_meta (EventMeta): Metadata object including trace_id and span_id.
    """
    def __init__(self, raw_message: dict):
        self.raw_message = raw_message
        self.event_name = raw_message.get("event_name")

        # event payload will contain entity_id, connector_id and other info
        # needed for specific events
        self.event_payload: dict = raw_message.get("event_payload", {})
        self.event_payload_path = raw_message.get("event_payload_path", False)

        # initialize EventMeta object
        self.event_meta = EventMeta(raw_message.get("event_meta", {}))

        # update raw message to include generated span_id
        self.raw_message["event_meta"] = self.event_meta.to_dict()

    def to_json(self) -> str:
        """
        Convert the event message to a JSON string.
        
        Returns:
            str: JSON string representation of the event message
        """
        message_dict = {
            "event_name": self.event_name,
            "event_payload": self.event_payload,
            "event_meta": self.event_meta.to_dict()
        }
        return json.dumps(message_dict)


class NATSEventMessage(EventMessage):
    """Handler for event messages received from NATS message broker.
    
    This class extends EventMessage to handle NATS-specific message format
    and provides access to the original NATS message object.
    
    Attributes:
        message_object (Msg): Original NATS message object
    """
    def __init__(self, message_object: Msg):
        # decode message data from NATs and parse it as JSON
        event_data: dict = json.loads(message_object.data.decode())
        super().__init__(event_data)
        self.message_object = message_object


class AWSEventMessage(EventMessage):
    """Handler for event messages received from AWS SQS.
    
    This class extends EventMessage to handle AWS SQS-specific message format
    and provides access to the SQS receipt handle for message acknowledgment.
    
    Attributes:
        receipt_handle (str): SQS receipt handle used for message acknowledgment
    """
    def __init__(self, raw_message: dict):
        sqs_message_body: dict = json.loads(raw_message.get("Body", "{}"))
        super().__init__(sqs_message_body.get("detail"))
        self.receipt_handle = raw_message.get("ReceiptHandle")


class AzureEventMessage(EventMessage):
    """Handler for event messages received from Azure Service Bus Queue.
    
    This class extends EventMessage to handle Azure Queue-specific message format
    and provides access to the Azure message id for message acknowledgment.
    
    Attributes:
        id (str): Azure Service Bus Queu message id used for message acknowledgment
    """
    def __init__(self, raw_message: dict):
        message_body: dict = json.loads(raw_message.get("data", "{}"))
        super().__init__(message_body)
        self.id = raw_message.get("id")
        