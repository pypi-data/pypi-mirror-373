"""
File name: s3_job_storage_manager.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Implemented factory pattern for batch job handler
"""

from shared_kernel.interfaces.storage_manager import JobStorageManager
from shared_kernel.logger import Logger
from shared_kernel.config import Config
from shared_kernel.storage_handlers.s3_storage_handler import S3FileHandler

config = Config()
logger = Logger(config.get("APP_NAME"))


class S3JobStorageManager(JobStorageManager):
    """
    S3-based storage manager for batch jobs.
    Handles uploading and downloading of job input payloads and results to/from S3.
    """
    def __init__(self, job_type: str, storage_root_folder : str = "batch_jobs"):
        """
        Initializes the S3 storage manager.

        Args:
            job_type (str): Type of the job (used to organize S3 paths).
            storage_root_folder (str): Base S3 prefix for all jobs.
        """
        self.s3_handler = S3FileHandler()
        self.storage_root_folder  = storage_root_folder 
        self.job_type = job_type

    def get_s3_key(self, job_storage_key: str) -> str:
        """
        Constructs the base S3 key for a given job.

        Args:
            job_storage_key (str): Unique job storage identifier.

        Returns:
            str: Base S3 key for the job folder.
        """
        return f"{self.storage_root_folder }/{self.job_type}/{job_storage_key}"

    def upload_payload(self, job_storage_key: str, payload: dict) -> str:
        """
        Uploads the job input payload (input.json) to S3.

        Args:
            job_storage_key (str): Unique job storage identifier.
            payload (dict): The job input payload.

        Returns:
            str: The S3 key where the payload was uploaded.

        Raises:
            Exception: If the S3 upload fails.
        """
        s3_key = self.get_s3_key(job_storage_key)
        s3_input_key = f"{s3_key}/input.json"

        try:
            if not self.s3_handler.upload_json(key=s3_input_key, data=payload):
                raise Exception("Upload returned False")
            logger.info(f"Uploaded job input to s3://{self.s3_handler.bucket}/{s3_input_key}")
            return s3_input_key
        except Exception as e:
            logger.error(f"Failed to upload payload for job_storage_key={job_storage_key}: {str(e)}")
            raise

    def upload_result(self, job_storage_key: str, result: dict) -> str:
        """
        Uploads the job result data (output.json) to S3.

        Args:
            job_storage_key (str): Unique job storage identifier.
            result (dict): The job result data.

        Returns:
            str: The S3 key where the result was uploaded.

        Raises:
            Exception: If the S3 upload fails.
        """
        s3_key = self.get_s3_key(job_storage_key)
        s3_output_key = f"{s3_key}/output.json"

        try:
            self.s3_handler.upload_json(s3_output_key, result)
            logger.info(f"Uploaded job result to s3://{self.s3_handler.bucket}/{s3_output_key}")
            return s3_output_key
        except Exception as e:
            logger.error(f"Failed to upload result for job_storage_key={job_storage_key}: {str(e)}")
            raise

    def download_input(self, job_storage_key: str) -> dict:
        """
        Downloads the input payload (input.json) for a job from S3.

        Args:
            job_storage_key (str): Unique job storage identifier.

        Returns:
            dict: The downloaded input payload.

        Raises:
            Exception: If the download fails.
        """
        s3_key = self.get_s3_key(job_storage_key)
        s3_input_key = f"{s3_key}/input.json"

        try:
            data = self.s3_handler.download_json(s3_input_key)
            logger.info(f"Downloaded job input from s3://{self.s3_handler.bucket}/{s3_input_key}")
            return data
        except Exception as e:
            logger.error(f"Failed to download input for job_storage_key={job_storage_key}: {str(e)}")
            raise

    def download_result(self, job_storage_key: str) -> dict:
        """
        Downloads the job result (output.json) from S3.

        Args:
            job_storage_key (str): Unique job storage identifier.

        Returns:
            dict: The downloaded job result.

        Raises:
            Exception: If the download fails.
        """
        s3_key = self.get_s3_key(job_storage_key)
        s3_output_key = f"{s3_key}/output.json"

        try:
            result = self.s3_handler.download_json(s3_output_key)
            logger.info(f"Downloaded job result from s3://{self.s3_handler.bucket}/{s3_output_key}")
            return result
        except Exception as e:
            logger.error(f"Failed to download result for job_storage_key={job_storage_key}: {str(e)}")
            raise
