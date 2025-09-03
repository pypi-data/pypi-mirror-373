"""
Filename: job_executor.py
Author: Akdham
Description: Handles the execution of individual jobs/tasks triggered by events.
Date: 2025-05-07
"""
from datetime import datetime
import json
from typing import Any, Callable, Dict, Optional

from shared_kernel.config import Config
from shared_kernel.enums import TaskStatus
from shared_kernel.exceptions.user_intervention_exception import UserInterventionRequiredError
from shared_kernel.interfaces import DataBus
from shared_kernel.logger import Logger
from shared_kernel.status_tracker import StatusTracker
from shared_kernel.messaging.utils.event_messages import AWSEventMessage, EventMessage
from shared_kernel.traceability.traceability_handler import Traceability
from shared_kernel.utils.thread_local_storage import ThreadLocalStorage
from shared_kernel.utils.thread_log_traker import LogStorage

app_config = Config()
logger = Logger(app_config.get("APP_NAME"))

thread_local_storage = ThreadLocalStorage()


class JobExecutor:
    """
    Handles the execution of individual jobs/tasks triggered by events.
    Responsible for the actual business logic execution and status tracking as well as error handling.
    """

    def __init__(self, status_tracker: StatusTracker, databus: DataBus):
        """
        Initialize the job executor.

        Args:
            status_tracker: Status tracker to track status of events' jobs
            databus: DataBus
        """
        self.status_tracker = status_tracker
        self.databus = databus

    def _setup_thread_context(self, event_msg: EventMessage) -> None:
        """
        Set up thread-local storage with event metadata.
        
        Args:
            event_msg: Event message containing metadata
        """
        context = {
            "trace_id": event_msg.event_meta.trace_id,
            "span_id": event_msg.event_meta.span_id,
            "event_name": event_msg.event_name,
            "event_payload": json.dumps(event_msg.event_payload),
            "event_meta": json.dumps(event_msg.event_meta.to_dict()),
        }
        
        # add optional fields if they exist
        if hasattr(event_msg.event_meta, "org_id"):
            context["org_id"] = event_msg.event_meta.org_id
            
        if hasattr(event_msg.event_meta, "trigger"):
            context["trigger"] = event_msg.event_meta.trigger
            
        if hasattr(event_msg.event_meta, "parent_span_id"):
            context["parent_span_id"] = event_msg.event_meta.parent_span_id
        
        thread_local_storage.set_all(context)
        logger.info("Event received", type="distributed_trace")

    def _get_task_tracking_id(self, task_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract tracking id from task details if available.
        
        Args:
            task_details: Task details dictionary
            
        Returns:
            tracking id or None
        """
        task = task_details.get("task_details") if task_details else None
        if task and task.get("tracking_id"):
            return json.loads(task["tracking_id"])
        return None
    
    def _is_duplicate_task(self, task_details: Optional[dict]) -> bool:
        return bool(task_details and task_details.get("is_duplicate", False))
    
    def _handle_new_task(self, event_msg: EventMessage):
        """
        Create a new task and set event meta and message receipt handle.
        
        Args:
            event_msg: Event message
        """
        logger.info(
            f"[JobExecutor] Creating new task:\n"
            f"  event_name: {event_msg.event_name}\n"
            f"  trace_id: {event_msg.event_meta.trace_id}\n"
            f"  span_id: {event_msg.event_meta.span_id}"
        )
        self.status_tracker.create_task(event_msg=event_msg, status=TaskStatus.PROCESSING.value)
        self.status_tracker.set_event_meta_and_message_receipt_handle(event_msg)

    def _update_queued_task(self, event_msg: EventMessage):
        """
        Update a queued task and set event meta and message receipt handle.
        
        Args:
            event_msg: Event message
        """
        logger.info(
            f"[JobExecutor] Updating queued task:\n"
            f"  event_name: {event_msg.event_name}\n"
            f"  trace_id: {event_msg.event_meta.trace_id}\n"
            f"  span_id: {event_msg.event_meta.span_id}"
        )
        self.status_tracker.set_event_meta_and_message_receipt_handle(event_msg)
        self.status_tracker.update_task(event_msg=event_msg, start_time=str(datetime.now()), status=TaskStatus.PROCESSING.value)

    def _handle_dlq(self, event_msg: EventMessage):
        """
        Publish event to DLQ.
        
        Args:
            event_msg: Event message
        """
        logger.warning(
            f"[JobExecutor] Publishing event to DLQ:\n"
            f"  event_name: {event_msg.event_name}\n"
            f"  trace_id: {event_msg.event_meta.trace_id}\n"
            f"  span_id: {event_msg.event_meta.span_id}"
        )
        self.databus.publish_event("DLQ", {
            "event_name": event_msg.event_name,
            "event_payload": event_msg.event_payload,
            "event_meta": event_msg.event_meta.to_dict(),
        })
    
    def _check_and_update_task_status(self, event_msg: AWSEventMessage) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Determines task state, returns whether it's a duplicate and tracking ID if needed.

        Args:
            event_msg: Event message

        Returns:
            tuple: (is_duplicate, tracking_id)
        """
        is_duplicate_task = False
        tracking_id = None

        logger.info(
            f"[JobExecutor] Checking task status:\n"
            f"  event_name: {event_msg.event_name}\n"
            f"  trace_id: {event_msg.event_meta.trace_id}\n"
            f"  span_id: {event_msg.event_meta.span_id}"
        )

        task_details: dict = self.status_tracker.get_task(task_details=event_msg)

        # check if the task is marked as a duplicate
        if self._is_duplicate_task(task_details):
            logger.info(
                f"[JobExecutor] Duplicate task already in progress:\n"
                f"  event_name: {event_msg.event_name}\n"
                f"  trace_id: {event_msg.event_meta.trace_id}\n"
                f"  span_id: {event_msg.event_meta.span_id}"
            )
            # mark the task as skipped & set the is_duplicate_task flag to True
            self.status_tracker.mark_as_skipped_if_duplicate_task(task_details=event_msg)
            is_duplicate_task = True
            return is_duplicate_task, tracking_id

        task = task_details.get("task_details") if task_details else None

        # task does not exist -> this is a new/fresh task
        if not task:
            logger.info(
                f"[JobExecutor] No existing task found, treating as new:\n"
                f"  event_name: {event_msg.event_name}\n"
                f"  trace_id: {event_msg.event_meta.trace_id}\n"
                f"  span_id: {event_msg.event_meta.span_id}"
            )
            self._handle_new_task(event_msg)

        # task exists and is in QUEUED state 
        # -> first execution attempt, possibly re-queued from restart mechanism
        # update in to PROCESSING state and get tracking id
        elif task["status"] == TaskStatus.QUEUED.value:
            logger.info(
                f"[JobExecutor] Task is queued, updating to processing:\n"
                f"  event_name: {event_msg.event_name}\n"
                f"  trace_id: {event_msg.event_meta.trace_id}\n"
                f"  span_id: {event_msg.event_meta.span_id}"
            )
            self._update_queued_task(event_msg)
            tracking_id = self._get_task_tracking_id(task_details)

        # task exists and is in PROCESSING state -> execution started earlier but was interrupted
        # so just get the tracking id
        elif task["status"] == TaskStatus.PROCESSING.value:
            logger.info(
                f"[JobExecutor] Task is already in processing:\n"
                f"  event_name: {event_msg.event_name}\n"
                f"  trace_id: {event_msg.event_meta.trace_id}\n"
                f"  span_id: {event_msg.event_meta.span_id}"
            )
            tracking_id = self._get_task_tracking_id(task_details)

        return is_duplicate_task, tracking_id
    
    def _handle_failure(self, event_msg: EventMessage, exception: Exception):
        """
        Handles failure reporting, tracking, and DLQ publishing.

        Args:
            event_msg: The event being processed
            exception: The exception that occurred
        """
        logger.error(
            f"[JobExecutor] Error processing event:\n"
            f"  event_name: {event_msg.event_name}\n"
            f"  trace_id: {event_msg.event_meta.trace_id}\n"
            f"  span_id: {event_msg.event_meta.span_id}\n"
            f"  error: {str(exception)}"
        )
        event_msg.event_meta.failure_reason = str(exception)

        status = (
            TaskStatus.USER_INTERVENTION_REQUIRED.value
            if isinstance(exception, UserInterventionRequiredError)
            else None
        )

        self.status_tracker.mark_task_as_failure(
            span_id=event_msg.event_meta.span_id,
            trace_id=event_msg.event_meta.trace_id,
            task=event_msg.event_name,
            failure_reason=str(exception),
            task_id=event_msg.event_meta.job_id,
            status=status
        )
        
        # handle trace to failure
        trace_id = event_msg.event_meta.trace_id
        tracebility_handler = Traceability(trace_id)
        tracebility_handler.mark_trace_as_failure()
        
        # NOTE: for dead letter queue we are simply publishing the
        # failed event to the databus as a DLQ event.
        self._handle_dlq(event_msg)

    def submit_job(self, callback: Callable, event_msg: AWSEventMessage) -> None:
        """
        Combined method to process message and handle status updates and cleanup.

        Args:
            callback: Callback function to invoke
            event_msg: Event message to process
        """
        is_success = False
        try:
            logger.info(
                f"[JobExecutor] Initiating event handling:\n"
                f"  event_name: {event_msg.event_name}\n"
                f"  event_payload: {event_msg.raw_message}\n"
                f"  trace_id: {event_msg.event_meta.trace_id}\n"
                f"  span_id: {event_msg.event_meta.span_id}"
            )

            # start event timing
            event_msg.event_meta.start_event_timer()
            logger.info(
                f"[JobExecutor] Event timer started:\n"
                f"  event_name: {event_msg.event_name}\n"
                f"  trace_id: {event_msg.event_meta.trace_id}\n"
                f"  span_id: {event_msg.event_meta.span_id}"
            )

            # thread-local storage
            self._setup_thread_context(event_msg)

            is_duplicate_task, tracking_id = self._check_and_update_task_status(event_msg=event_msg)

            if is_duplicate_task:
                logger.info(
                    f"[JobExecutor] Skipping execution for duplicate task:\n"
                    f"  event_name: {event_msg.event_name}\n"
                    f"  trace_id: {event_msg.event_meta.trace_id}\n"
                    f"  span_id: {event_msg.event_meta.span_id}"
                )
                return

            # pass the actual message to the callback rather than the event message object
            callback(event_msg.raw_message, tracking_id)
            is_success = True

        except Exception as e:
            self._handle_failure(event_msg, e)

        finally:
            event_msg.event_meta.end_event_timer()
            self.status_tracker.set_event_meta_and_message_receipt_handle(event_msg)

            if is_success:
                logger.info(
                    f"[JobExecutor] Event processed successfully:\n"
                    f"  event_name: {event_msg.event_name}\n"
                    f"  trace_id: {event_msg.event_meta.trace_id}\n"
                    f"  span_id: {event_msg.event_meta.span_id}"
                )
                self.status_tracker.update_task(event_msg=event_msg, status=TaskStatus.COMPLETED.value)
            else:
                logger.error(
                    f"[JobExecutor] Event processing failed:\n"
                    f"  event_name: {event_msg.event_name}\n"
                    f"  trace_id: {event_msg.event_meta.trace_id}\n"
                    f"  span_id: {event_msg.event_meta.span_id}"
                )
            LogStorage().clean_log(track_id=event_msg.event_meta.span_id)
            thread_local_storage.clear()
            self.databus.delete_message(event_msg)
