"""
File name: job_context.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Implemented factory pattern for batch job handler
"""

from dataclasses import dataclass
from typing import Optional, Dict
from shared_kernel.batch_job.job_handlers.job_status_mapper import JOB_STATUS_TO_TASK_STATUS
from shared_kernel.messaging.utils.event_messages import EventMessage
from shared_kernel.enums.status_tracker import TaskStatus
from dataclasses import field

@dataclass
class JobContext:
    """
    Base context for any job (e.g., AWS Batch).

    Attributes:
        task_id (str): Unique identifier for the task/job, used for status tracking.
        job_type (str): Business or functional category of the job (e.g., "METRIC_ANOMALY_DETECTION").
        job_runner (str): The execution backend responsible for running the job (e.g., "AWS_BATCH").
        job_storage_key (str): Unique identifier for job data storage (e.g., S3 key).
        job_storage_type (str): Storage backend type (e.g., "s3").
        event_meta (Dict[str, str]): Metadata for tracing, logging, and event messages.
        job_status (Optional[TaskStatus]): Current internal status of the job.
    """
    task_id: str
    job_type: str
    job_runner: str
    job_storage_key: str
    job_storage_type: str
    
    event_meta: Dict[str, str] = field(default_factory=dict)
    job_status: Optional[TaskStatus] = None

    def to_status_event(self) -> EventMessage:
        """
        Creates an EventMessage representing this job's current status.

        Returns:
            EventMessage: A status tracking event containing job type and metadata.
        """
        return EventMessage(
            raw_message={
                "event_name": self.job_type,
                "event_meta": {**self.event_meta, "job_id": self.task_id}
            }
        )

    def get_failure_event_info(self, failure_reason: str) -> dict:
        """
        Prepares failure information to log in the status tracker.

        Args:
            failure_reason (str): A descriptive reason for the job failure.

        Returns:
            dict: A dictionary containing trace IDs, task identifiers, and failure reason.
        """
        return {
            "span_id": self.event_meta.get("span_id"),
            "trace_id": self.event_meta.get("trace_id"),
            "task": self.job_type,
            "failure_reason": failure_reason,
            "task_id": self.task_id
        }
    
    def update_job_status(self, status: str):
        """
        Updates the internal job_status based on the AWS Batch status string.

        Args:
            status (str): AWS Batch job status (e.g., 'SUCCEEDED', 'FAILED').

        Raises:
            ValueError: If the provided status is not recognized.
        """
        mapped_status = JOB_STATUS_TO_TASK_STATUS.get(status)
        if not mapped_status:
            raise ValueError(f"Unrecognized AWS job status: {status}")
        self.job_status = mapped_status

