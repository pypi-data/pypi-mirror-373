"""
File name: aws_batch_job_handler.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Implemented factory pattern for batch job handler
"""

import boto3
import time
from shared_kernel.batch_job.job_handlers.job_status_mapper import JOB_STATUS_TO_TASK_STATUS
from shared_kernel.config import Config
from shared_kernel.dataclasses.aws_batch_job_context import AWSBatchJobContext
from shared_kernel.exceptions.batch_job_exceptions import BatchJobFailedException
from shared_kernel.interfaces.base_job_handler import BaseJobHandler
from shared_kernel.interfaces.storage_manager import JobStorageManager
from shared_kernel.logger import Logger
from shared_kernel.status_tracker.status_tracker import StatusTracker
from shared_kernel.enums.status_tracker import TaskStatus


config = Config()
logger = Logger(config.get("APP_NAME"))
AWS_REGION =  config.get("AWS_REGION")
DATALAKE_BUCKET = config.get("FDC_DATA_LAKE_BUCKET")

class AWSBatchJobHandler(BaseJobHandler):
    """
    Handles the lifecycle of AWS Batch jobs with S3-based payload exchange.

    Core Responsibilities:
    - Submitting AWS Batch jobs with the given configuration.
    - Polling job status until completion or failure.
    - Uploading input payloads to the configured storage.
    - Downloading job results from the configured storage.
    - Updating and tracking job status using StatusTracker.
    """
    def __init__(self, storage_manager:JobStorageManager):
        """
        Initialize the AWSBatchJobHandler.

        Args:
            storage_manager (JobStorageManager): The storage manager for payload and result handling.
        """
        self.batch_client = boto3.client("batch", region_name=AWS_REGION)
        self.storage_manager: JobStorageManager = storage_manager
        self.status_tracker = StatusTracker()

    def submit_job(self, job_context: AWSBatchJobContext) -> str:
        """
        Submit an AWS Batch job with the provided configuration.

        Args:
            job_context (AWSBatchJobContext): Context containing job name, queue, 
                                              job definition, and environment variables.

        Returns:
            str: The AWS Batch job ID assigned to the submitted job.

        Raises:
            BatchJobFailedException: If the job submission fails or no job ID is returned.
            Exception: For unexpected AWS API or network errors.
        """
        try:
            job_payload = job_context.to_batch_payload()
            response = self.batch_client.submit_job(**job_payload)
            job_id = response["jobId"]
            if not job_id:
                raise BatchJobFailedException(
                    job_type=job_context.job_type,
                    job_id=None,
                    job_name=job_context.job_name,
                    reason="Batch job submission did not return a job ID."
                )
            job_context.job_id = job_id
            logger.info(f"Submitted AWS Batch job {job_context.job_name} with ID {job_id}")
            self.status_tracker.create_task(event_msg=job_context.to_status_event(), status=TaskStatus.QUEUED.value)
            return job_id
        except BatchJobFailedException as e:
            raise
        except Exception as e:
            logger.error(f"Failed to submit AWS Batch job {job_context.job_name}: {str(e)}")
            raise

    def wait_for_job_completion(
        self,
        job_context: AWSBatchJobContext,
        timeout: int = 180,
        poll_interval: int = 10
    ) -> None:
        """
        Poll AWS Batch for job completion status.

        Args:
            job_context (AWSBatchJobContext): Context containing job details, including job ID.
            timeout (int): Maximum time (in seconds) to wait for the job to complete. Default is 180 seconds.
            poll_interval (int): Time interval (in seconds) between each polling request. Default is 10 seconds.

        Raises:
            TimeoutError: If the job does not complete within the given timeout.
            BatchJobFailedException: If the job fails during execution.
            Exception: For unexpected errors while polling AWS Batch.
        """
        start_time = time.time()
        while True:
            try:
                response = self.batch_client.describe_jobs(jobs=[job_context.job_id])
                job_detail = response["jobs"][0]
                status_str = job_detail["status"]
                new_status = JOB_STATUS_TO_TASK_STATUS.get(status_str)
                if new_status and new_status != job_context.job_status:
                    logger.info(f"Job {job_context.job_id} status changed from {job_context.job_status} to {new_status.value}")
                    self.status_tracker.update_task(
                        event_msg=job_context.to_status_event(),
                        status=new_status.value
                    )
                    job_context.job_status = new_status

                if status_str == "SUCCEEDED":
                    logger.info(f"Job {job_context.job_id} completed successfully.")
                    return

                if status_str == "FAILED":
                    self.handle_failed_batch_job(job_context=job_context, job_detail=job_detail)

                if time.time() - start_time > timeout:
                    logger.error(f"Timeout waiting for job {job_context.job_id}")
                    raise TimeoutError(f"Job {job_context.job_id} did not complete within {timeout} seconds.")

                time.sleep(poll_interval)
            except BatchJobFailedException as e:
                raise
            except Exception as e:
                logger.error(f"Error while polling job {job_context.job_id}: {str(e)}")
                raise
    
    def process_job(self, payload: dict, job_context: AWSBatchJobContext) -> dict:
        """
        Orchestrates the entire AWS Batch job lifecycle:
        - Uploads the input payload to storage.
        - Submits the AWS Batch job.
        - Waits for the job to complete.
        - Downloads and returns the job result.

        Args:
            payload (dict): Input payload to upload to the storage manager.
            job_context (AWSBatchJobContext): The job context containing all required configurations.

        Returns:
            dict: The job's output data.

        Raises:
            BatchJobFailedException: If the job fails or no valid output is available.
        """
        try:
            logger.info(f"Starting batch job process for: {job_context.job_name}")
            self.storage_manager.upload_payload(job_storage_key=job_context.job_storage_key, payload=payload)
            self.submit_job(job_context=job_context)
            self.wait_for_job_completion(job_context=job_context)
            result = self.storage_manager.download_result(job_storage_key=job_context.job_storage_key)
            if not result or not isinstance(result, dict):
                raise BatchJobFailedException(
                    job_type=job_context.job_type,
                    job_id=job_context.job_id,
                    job_name=job_context.job_name,
                    reason="Job succeeded but no output found in configured storage"
                )
            if result.get("error"):
                raise BatchJobFailedException(
                    job_type=job_context.job_type,
                    job_id=job_context.job_id,
                    job_name=job_context.job_name,
                    reason=result.get("message")
                )
            logger.info(f"Completed batch job process for: {job_context.job_name}")
            return result.get("data")
        except BatchJobFailedException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch result for {job_context.job_name}: {str(e)}")
            raise BatchJobFailedException(
                job_type=job_context.job_type,
                job_id=job_context.job_id,
                job_name=job_context.job_name,
                reason=f"{str(e)}"
            )
    
    def handle_failed_batch_job(self, job_detail: dict, job_context: AWSBatchJobContext):
        """
        Handles AWS Batch job failures by:
        - Extracting the failure reason.
        - Logging the failure.
        - Updating the StatusTracker with failure details.
        - Raising a BatchJobFailedException.

        Args:
            job_detail (dict): AWS Batch job details as returned by describe_jobs().
            job_context (AWSBatchJobContext): Context of the failed job.

        Raises:
            BatchJobFailedException: Always raised after failure handling.
        """
        failure_reason = self._extract_failure_reason(job_detail=job_detail, job_context=job_context)
        logger.error(f"Job {job_context.job_id} failed during execution due to {failure_reason}.")
        self.status_tracker.mark_task_as_failure(
            **job_context.get_failure_event_info(failure_reason)
        )
        raise BatchJobFailedException(job_type=job_context.job_type,
                                    job_id=job_context.job_id,
                                    reason=failure_reason,
                                    job_name=job_context.job_name)
        
        
    def _extract_failure_reason(self, job_detail: dict, job_context: AWSBatchJobContext) -> str:
        """
        Extract the failure reason for a job by:
        1. Attempting to download the result from storage.
        2. Falling back to the AWS Batch status reason if no result is available.

        Args:
            job_detail (dict): AWS Batch job detail dictionary.
            job_context (AWSBatchJobContext): Job context for accessing storage.

        Returns:
            str: A human-readable failure reason.
        """
        failure_reason = None

        # Step 1: Try downloading result from S3 (best-effort)
        try:
            result = self.storage_manager.download_result(job_storage_key=job_context.job_storage_key)
            if result and result.get("error"):
                failure_reason = result.get("message")
        except Exception as e:
            logger.warning(f"[Failure Reason Fallback] Could not download failure result from S3 for job {job_context.job_id}: {str(e)}")

        if not failure_reason:
            failure_reason = job_detail.get("statusReason")
        return failure_reason