"""
File name: job_handler_factory.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Implemented factory pattern for batch job handler
"""

from shared_kernel.batch_job.job_handlers.aws_batch_job_handler import AWSBatchJobHandler
from shared_kernel.dataclasses.job_context import JobContext
from shared_kernel.exceptions.batch_job_exceptions import BatchJobFailedException
from shared_kernel.interfaces.storage_manager import JobStorageManager


class JobHandlerFactory:
    """
    Factory class responsible for creating appropriate job handler instances
    based on the job type defined in the JobContext.

    This allows adding support for new job execution backends (e.g., AWS Batch) without changing existing client code.
    """
    @staticmethod
    def get_handler(job_runner: str, storage_manager:JobStorageManager):
        """
        Creates and returns a job handler instance for the given job type.

        Args:
            job_context (JobContext): The context containing details about the job
                                      (e.g., job_type, job_name, storage key).
            storage_manager (JobStorageManager): Manager responsible for 
                                                 uploading/downloading job data.

        Returns:
            BaseJobHandler: An instance of a job handler matching the job_type.

        Raises:
            BatchJobFailedException: If no handler is registered for the provided job_type.
        """

        if job_runner == "AWS_BATCH":
            return AWSBatchJobHandler(storage_manager=storage_manager)
        
        raise BatchJobFailedException(
            job_type=None,
            job_id=None,
            job_name=None,
            reason=f"No job handler found for {job_runner} type jobs"
        )