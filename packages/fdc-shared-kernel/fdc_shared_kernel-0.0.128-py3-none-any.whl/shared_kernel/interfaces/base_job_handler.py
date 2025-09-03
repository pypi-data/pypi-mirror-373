from abc import ABC, abstractmethod
from shared_kernel.dataclasses.job_context import JobContext


class BaseJobHandler(ABC):
    """
    Abstract base class defining the contract for job execution and lifecycle management.

    This class provides a unified interface for different job execution backends,
    such as AWS Batch, ensuring consistent handling of job submission, polling,
    and result retrieval.

    Methods
    -------
    submit_job(job_context: JobContext) -> str:
        Submits a job to the backend and returns a unique job ID.

    wait_for_job_completion(job_context: JobContext, timeout: int = 180, poll_interval: int = 10) -> None:
        Polls the job status until completion or failure, with configurable timeout and polling intervals.

    process_job(job_context: JobContext, payload: dict) -> dict:
        Orchestrates the full job lifecycle:
        - Submits the job.
        - Waits for completion.
        - Retrieves and returns the final job result.
    """

    @abstractmethod
    def submit_job(self, job_context: JobContext) -> str:
        """
        Submits a job using the provided job context.

        Args:
            job_context (JobContext): Context containing job details such as type, name, and configuration.

        Returns:
            str: A unique identifier (job ID) for the submitted job.
        """
        pass

    @abstractmethod
    def wait_for_job_completion(self, job_context: JobContext, timeout: int = 180, poll_interval: int = 10) -> None:
        """
        Waits for the completion or failure of a submitted job.

        Args:
            job_context (JobContext): Context containing the job ID to track.
            timeout (int): Maximum time (in seconds) to wait before timing out. Default is 180 seconds.
            poll_interval (int): Time interval (in seconds) between job status checks. Default is 10 seconds.
        """
        pass

    @abstractmethod
    def process_job(self, job_context: JobContext, payload: dict) -> dict:
        """
        Orchestrates the full job lifecycle:
        - Uploads input payload (if applicable).
        - Submits the job.
        - Waits for completion or failure.
        - Fetches and returns the job output.

        Args:
            job_context (JobContext): Context containing job details and configuration.
            payload (dict): Input data payload for the job.

        Returns:
            dict: The final output data from the job.
        """
        pass