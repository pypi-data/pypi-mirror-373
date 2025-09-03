import json
from shared_kernel.exceptions.custom_exceptions import StatusTrackerException
from shared_kernel.interfaces.databus import DataBus
from shared_kernel.messaging import DataBusFactory
from shared_kernel.messaging.utils.event_messages import EventMessage
from shared_kernel.registries.service_event_registry import ServiceEventRegistry

service_event_registry = ServiceEventRegistry()


class StatusTracker:
    """
    A singleton StatusTracker class that ensures only one StatusTracker instance is created.

    Attributes:
        _instance (Optional[StatusTracker]): The single instance of the StatusTracker.
    """

    _instance = None

    def __new__(cls):
        """
        override __new__ to ensure singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(StatusTracker, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self):
        self.databus: DataBus = DataBusFactory.create_data_bus(
            bus_type="HTTP", config={}
        )


    def create_task(self, event_msg: EventMessage, status):
        """Publishes a synchronous event to create a task"""
        try:
            payload = {
                "span_id": event_msg.event_meta.span_id,
                "trace_id": event_msg.event_meta.trace_id,
                "task": event_msg.event_name,
                "status": status,
                "task_id": event_msg.event_meta.job_id,
                "org_id": event_msg.event_meta.org_id,
            }
            if event_msg.event_meta.entity_id:
                payload["entity_id"] = event_msg.event_meta.entity_id
            response = self.databus.request_event(
                getattr(service_event_registry, "CREATE_TASK"), payload
            )
            return response

        except Exception as e:
            raise StatusTrackerException(e)


    def update_task(self, event_msg: EventMessage, start_time = None, status = None, misc_data=None):
        """Publishes a synchronous event to update a task"""
        try:
            payload = {
                "span_id": event_msg.event_meta.span_id,
                "trace_id": event_msg.event_meta.trace_id,
                "task": event_msg.event_name,
                "status": status,
                "task_id": event_msg.event_meta.job_id,
                "start_time": start_time,
                "misc_data": misc_data
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "UPDATE_TASK"), payload
            )
            return response

        except Exception as e:
            raise StatusTrackerException(e)


    def mark_task_as_failure(self, span_id, trace_id, task, failure_reason, task_id, status=None):
        """Publishes a synchronous event to mark a task as failure"""
        try:
            payload = {
                "span_id": span_id,
                "trace_id": trace_id,
                "task": task,
                "failure_reason": failure_reason,
                "task_id": task_id,
                "status": status
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "MARK_TASK_AS_FAILURE"), payload
            )
            return response

        except Exception as e:
            raise StatusTrackerException(e)
        
    
    def get_task(self, task_details: EventMessage):
        """Publishes a synchronous event to retrieve a task"""
        try:
            payload = {
                "task": task_details.event_name,
                "task_id": task_details.event_meta.job_id,
                "entity_id": task_details.event_meta.entity_id if task_details.event_meta.entity_id else None,
                "trace_id": task_details.event_meta.trace_id,
                "span_id": task_details.event_meta.span_id,
                "org_id": task_details.event_meta.org_id,
            }
            response: dict = self.databus.request_event(
                getattr(service_event_registry, "GET_TASK"), payload
            )
            return response.get("data")

        except Exception as e:
            raise StatusTrackerException(e)
        
    
    def mark_as_skipped_if_duplicate_task(self, task_details: EventMessage):
        """Publishes a synchronous event to check for duplicate task"""
        try:
            response: dict = self.databus.request_event(
                getattr(service_event_registry, "MARK_TASK_AS_SKIPPED"), json.loads(task_details.to_json())
            )
            return response.get("data")

        except Exception as e:
            raise StatusTrackerException(e)

    
    def get_in_progress_task(self, task):
        """Publishes a synchronous event to retrieve a task in Processing status"""
        try:
            payload = {
                "task": task,
            }
            response: dict = self.databus.request_event(
                getattr(service_event_registry, "GET_IN_PROGRESS_TASK"), payload
            )
            return response.get("data")

        except Exception as e:
            raise StatusTrackerException(e)
        
    
    def set_event_meta_and_message_receipt_handle(self, event_msg: EventMessage):
        """Publishes a synchronous event to set event meta"""
        try:
            payload = {
                "event_meta": event_msg.event_meta.to_dict(),
                "task_id": event_msg.event_meta.job_id,
                "task": event_msg.event_name,
            }
            if hasattr(event_msg, "receipt_handle"):
                # check if event_msg has receipt_handle
                # this method is called with EventMessage as well AWSEventMessage
                # only instance of AWSEventMessage will have receipt_handle
                payload["message_receipt_handle"] = event_msg.receipt_handle

            response = self.databus.request_event(
                getattr(service_event_registry, "SET_EVENT_META_AND_MESSAGE_RECEIPT_HANDLE"), payload
            )
            return response

        except Exception as e:
            raise StatusTrackerException(e)
        
    
    def set_tracking_id(self, task_id, task, tracking_id):
        """Publishes a synchronous event to set tracking id"""
        try:
            payload = {
                "task_id": task_id,
                "task": task,
                "tracking_id": tracking_id,
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "SET_TRACKING_ID"), payload
            )
            return response

        except Exception as e:
            raise StatusTrackerException(e)


    def get_pending_tasks_by_trace_id(self, trace_id):
        """Publishes a synchronous event to get pending task by trace id"""
        try:
            payload = {
                "trace_id": trace_id,
            }
            response = self.databus.request_event(
                getattr(service_event_registry, "GET_PENDING_TASKS_BY_TRACE_ID"), payload
            )
            return response

        except Exception as e:
            raise StatusTrackerException(e)
          