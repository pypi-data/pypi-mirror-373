from abc import ABC, abstractmethod

class JobStorageManager(ABC):
    """
    Abstract base class that defines the contract for job storage operations,
    including uploading and downloading input payloads and output results.

    Implementations of this interface can use various backends (e.g., S3, 
    file system, database) to persist job data.

    Methods
    -------
    upload_payload(job_storage_key: str, payload: dict) -> str:
        Uploads the job's input payload to the storage system and returns 
        the storage path or key.

    download_result(job_storage_key: str) -> dict:
        Retrieves the job's output result from the storage system using 
        the provided storage key.

    upload_result(job_storage_key: str, result: dict) -> str:
        Uploads the job's result data to the storage system and returns 
        the storage path or key.

    download_input(job_storage_key: str) -> dict:
        Retrieves the input payload of a job from the storage system using 
        the provided storage key.
    """
    @abstractmethod
    def upload_payload(self, job_storage_key: str, payload: dict) -> str:
        """
        Uploads the job's input payload.

        Args:
            job_storage_key (str): Unique key or identifier for the job storage path.
            payload (dict): Input data to be uploaded.

        Returns:
            str: The storage path or key where the payload is stored.
        """
        pass

    @abstractmethod
    def download_result(self, job_storage_key: str) -> dict:
        """
        Downloads the job's output result.

        Args:
            job_storage_key (str): Unique key or identifier for the job storage path.

        Returns:
            dict: The job's output result data.
        """
        pass

    @abstractmethod
    def upload_result(self, job_storage_key: str, result: dict) -> str:
        """
        Uploads the job's result data.

        Args:
            job_storage_key (str): Unique key or identifier for the job storage path.
            result (dict): Result data to be uploaded.

        Returns:
            str: The storage path or key where the result is stored.
        """
        pass

    @abstractmethod
    def download_input(self, job_storage_key: str) -> dict:
        """
        Downloads the job's input payload.

        Args:
            job_storage_key (str): Unique key or identifier for the job storage path.

        Returns:
            dict: The job's input payload data.
        """
        pass