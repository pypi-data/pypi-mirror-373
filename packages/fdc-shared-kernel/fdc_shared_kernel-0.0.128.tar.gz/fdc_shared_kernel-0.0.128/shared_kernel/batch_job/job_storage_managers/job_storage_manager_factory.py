"""
File name: job_storage_manager_factory.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Implemented factory pattern for batch job handler
"""

from shared_kernel.batch_job.job_storage_managers.s3_job_storage_manager import S3JobStorageManager
from shared_kernel.interfaces.storage_manager import JobStorageManager

class JobStorageManagerFactory:
    """
    Factory class responsible for creating storage manager instances
    for different storage backends (e.g., S3).

    This abstraction allows switching storage implementations without
    changing the job handling logic.
    """
    @staticmethod
    def get_storage_manager(job_type: str, storage_type: str = "s3", storage_root_folder : str = "batch_jobs") -> JobStorageManager:
        """
        Returns an instance of a JobStorageManager based on the storage type.

        Args:
            job_type (str): The job type, used to organize results in storage
                            (e.g., results of the same job type will be stored
                            in the same folder).
            storage_type (str): The type of storage backend (default: "s3").
                                Supported values: "s3".
            storage_root_folder (str): Root folder for storing job data.

        Returns:
            JobStorageManager: An instance of a storage manager for the
                               specified storage type.

        Raises:
            ValueError: If the given storage_type is not supported.
        """
        if storage_type == "s3":
            return S3JobStorageManager(storage_root_folder=storage_root_folder, job_type=job_type)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
