"""
File name: aws_batch_job_context.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Implemented factory pattern for batch job handler
"""

from dataclasses import dataclass
from typing import Dict, Optional
from .job_context import JobContext

@dataclass
class AWSBatchJobContext(JobContext):
    """
    AWS Batch-specific job context.

    Attributes:
        job_name (str): Name of the AWS Batch job.
        job_queue (str): The AWS Batch job queue where the job will be submitted.
        job_definition (str): AWS Batch job definition to be used.
        job_id (Optional[str]): The AWS Batch job ID (assigned after submission).
        metadata (Optional[Dict[str, str]]): Additional environment variables 
                                            to pass to the job container.
        container_overrides (Optional[Dict]): Overrides for container resources 
                                              (e.g., vCPU, memory).
    """
    job_name: Optional[str] = None
    job_queue: Optional[str] = None
    job_definition: Optional[str] = None
    job_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None  # Additional env vars
    container_overrides: Optional[Dict] = None  # vCPU/memory overrides

    def __post_init__(self):
        """
        Validates that required AWS Batch fields are set.
        """
        if not self.job_name:
            raise ValueError("AWSBatchContext requires 'job_name' to be set.")
        if not self.job_queue:
            raise ValueError("AWSBatchJobContext requires 'job_queue' to be set.")
        if not self.job_definition:
            raise ValueError("AWSBatchJobContext requires 'job_definition' to be set.")

    def to_env_vars(self) -> Dict[str, str]:
        """
        Builds the set of environment variables for the AWS Batch container.

        Returns:
            Dict[str, str]: A dictionary of environment variables including:
                            - JOB_STORAGE_TYPE: Storage backend type (e.g., "s3").
                            - JOB_STORAGE_KEY: The S3 folder key for job data.
                            - JOB_TYPE: The type of the job.
                            - Any additional metadata keys (uppercased).
        """
        env = {
            "JOB_STORAGE_TYPE": self.job_storage_type,
            "JOB_STORAGE_KEY": self.job_storage_key,
            "JOB_TYPE": self.job_type
        }
        if self.metadata:
            env.update({k.upper(): str(v) for k, v in self.metadata.items()})
        return env
    
    def to_batch_payload(self) -> Dict[str, any]:
        """
        Constructs the AWS Batch job submission payload.

        Returns:
            Dict[str, any]: A dictionary containing:
                            - jobName: Name of the job.
                            - jobQueue: Target AWS Batch queue.
                            - jobDefinition: AWS Batch job definition.
                            - containerOverrides: Environment variables and 
                                                  resource overrides.
        """
        env_vars = [{"name": k, "value": v} for k, v in self.to_env_vars().items()]
        overrides = self.container_overrides or {}
        overrides["environment"] = env_vars

        return {
            "jobName": self.job_name,
            "jobQueue": self.job_queue,
            "jobDefinition": self.job_definition,
            "containerOverrides": overrides,
        }
