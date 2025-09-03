from datetime import datetime
from uuid import uuid4

from shared_kernel.exceptions.custom_exceptions import StatusTrackerException
from shared_kernel.exceptions.http_exceptions import NotFound
from shared_kernel.interfaces.databus import DataBus
from shared_kernel.messaging import DataBusFactory
from shared_kernel.registries.service_event_registry import ServiceEventRegistry

service_event_registry = ServiceEventRegistry()


class Traceability():
    """
    The `Traceability` class implements a singleton pattern and provides a method to create events 
    with traceability information.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        override __new__ to ensure singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(Traceability, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def __init__(self, trace_id: str = None, payload: dict = None):
        self.trace_id = trace_id or str(uuid4())
        self.payload = payload

    def _initialize(self):
        self.databus: DataBus = DataBusFactory.create_data_bus(
            bus_type="HTTP", config={}
        )

    def create(self):
        try:
            event_payload = {
                "trace_id": self.trace_id,
                **self.payload,
                "created_at": str(datetime.now()),
                "updated_at":str(datetime.now()),
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "CREATE_TRACE"), event_payload
            )
            return response
        except Exception as e:
            raise StatusTrackerException(e)


    def update(self, update_payload: dict):
        try:
            event_payload = {
                "trace_id": self.trace_id,
                **update_payload,
                "updated_at": str(datetime.now())
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "UPDATE_TRACE"), event_payload
            )
            return response
        except Exception as e:
            if ( (isinstance(e, NotFound)) or (str(e) == "Trace Not Found")):
                raise NotFound(str(e))
            raise StatusTrackerException(e)

    def mark_trace_as_failure(self):
        try:
            event_payload = {
                "trace_id": self.trace_id,
                "execution_status": "Failure"
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "UPDATE_TRACE"), event_payload
            )
            return response
        except Exception as e:
            raise StatusTrackerException(e)

    def mark_trace_as_completed(self):
        try:
            event_payload = {
                "trace_id": self.trace_id,
                "execution_status": "Completed"
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "UPDATE_TRACE"), event_payload
            )
            return response
        except Exception as e:
            raise StatusTrackerException(e)
