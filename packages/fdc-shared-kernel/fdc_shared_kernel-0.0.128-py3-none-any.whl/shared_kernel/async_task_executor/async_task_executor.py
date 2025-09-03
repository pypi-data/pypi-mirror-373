import uuid
import json
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from shared_kernel.enums.async_task_executor import AsyncTaskStatus
from shared_kernel.logger import Logger
from shared_kernel.config import Config


config = Config()
logger = Logger(config.get("APP_NAME"))


class AsyncTaskExecutor:
    """
    Singleton class for managing the execution of asynchronous tasks.
    It uses a thread pool to manage concurrency and a status tracker to monitor task execution.
    Supports both in-memory and file-based storage for task status.
    """

    _instance = None
    # lock to ensure thread safety
    _lock = Lock()

    def __new__(self, concurrency: int, use_file_storage: bool = False, storage_file_path: str = None):
        """
        Singleton method that ensures only one instance of AsyncTaskExecutor is created.
        Uses double-checked locking to ensure thread safety.

        Args:
            concurrency (int): The maximum number of threads allowed to run concurrently.
            use_file_storage (bool): Flag to determine if status should be stored in file (True) or memory (False).
            storage_file_path (str, optional): Custom path to the file for storing task status. If not provided, a default path will be used.

        Returns:
            AsyncTaskExecutor: A single instance of AsyncTaskExecutor.
        """
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = super(AsyncTaskExecutor, self).__new__(self)
                    self._instance._initialized = False
        return self._instance

    def __init__(self, concurrency: int, use_file_storage: bool = False, storage_file_path: str = None):
        """
        Initializes the AsyncTaskExecutor. This method will only run once for the singleton instance.

        Args:
            concurrency (int): The number of threads that can be run concurrently in the pool.
            use_file_storage (bool): Flag to determine if status should be stored in file (True) or memory (False).
            storage_file_path (str, optional): Custom path to the file for storing task status. If not provided, a default path will be used.
        """
        if self._initialized:
            return
        
        self.use_file_storage = use_file_storage
        
        if use_file_storage:
            # Define default storage file path if not provided
            if storage_file_path is None:
                task_status_dir = os.path.join(os.getcwd(), "async_tasks_status")
                os.makedirs(task_status_dir, exist_ok=True)
                self.storage_file_path = os.path.join(task_status_dir, "async_task_status.json")
            else:
                self.storage_file_path = storage_file_path
            
            os.makedirs(os.path.dirname(self.storage_file_path), exist_ok=True)
            if not os.path.exists(self.storage_file_path):
                self._save_status_to_file({})
            
            logger.info(f"AsyncTaskExecutor using file-based storage at: {self.storage_file_path}")
        else:
            # dictionary to track the status of tasks in memory
            self.status_tracker: dict = {}
            
        self.queue = ThreadPoolExecutor(max_workers=int(concurrency))
        # mark as initialized to prevent re-initialization
        self._initialized = True
        
        storage_mode = "file-based" if use_file_storage else "in-memory"
        logger.debug(
            f"AsyncTaskExecutor initialized with concurrency level: {concurrency}, storage mode: {storage_mode}"
        )

    def _save_status_to_file(self, status_data: dict):
        """
        Saves the status data to the file.
        
        Args:
            status_data (dict): The status data to save.
        """
        try:
            with open(self.storage_file_path, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status to file {self.storage_file_path}: {str(e)}")
            raise

    def _load_status_from_file(self) -> dict:
        """
        Loads the status data from the file.
        
        Returns:
            dict: The status data loaded from file.
        """
        try:
            if os.path.exists(self.storage_file_path):
                with open(self.storage_file_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load status from file {self.storage_file_path}: {str(e)}")
            return {}

    def _update_status(self, execution_id: str, status_data: dict):
        """
        Updates the status for a given execution ID.
        
        Args:
            execution_id (str): The execution ID to update.
            status_data (dict): The status data to set.
        """
        if self.use_file_storage:
            current_status = self._load_status_from_file()
            current_status[execution_id] = status_data
            self._save_status_to_file(current_status)
        else:
            self.status_tracker[execution_id] = status_data

    def _get_status(self, execution_id: str) -> dict:
        """
        Gets the status for a given execution ID.
        
        Args:
            execution_id (str): The execution ID to get status for.
            
        Returns:
            dict: The status data for the execution ID.
        """
        if self.use_file_storage:
            current_status = self._load_status_from_file()
            return current_status.get(execution_id, {"status": AsyncTaskStatus.NA.value})
        else:
            return self.status_tracker.get(execution_id, {"status": AsyncTaskStatus.NA.value})

    def _remove_status(self, execution_id: str):
        """
        Removes the status for a given execution ID.
        
        Args:
            execution_id (str): The execution ID to remove.
        """
        if self.use_file_storage:
            current_status = self._load_status_from_file()
            if execution_id in current_status:
                del current_status[execution_id]
                self._save_status_to_file(current_status)
        else:
            if execution_id in self.status_tracker:
                del self.status_tracker[execution_id]

    def task_execute_wrapper(self, task_to_execute, job_payload: dict):
        """
        Wrapper method to execute a task and handle its status updates.
        Updates the task's status to STARTED, SUCCESS, or FAILURE depending on the outcome.

        Args:
            task_to_execute (callable): The function representing the task to be executed.
            job_payload (dict): The payload containing job-related information, including the execution ID.
        """
        execution_id = job_payload["execution_id"]
        self._update_status(execution_id, {"status": AsyncTaskStatus.STARTED.value})
        logger.debug(f"Task started for execution ID: {execution_id}")
        try:
            result = task_to_execute(job_payload)
            self._update_status(execution_id, {
                "status": AsyncTaskStatus.SUCCESS.value,
                "data": result
            })
            logger.debug(
                f"Task completed successfully for execution ID: {execution_id}"
            )
        except Exception as e:
            self._update_status(execution_id, {
                "status": AsyncTaskStatus.FAILURE.value,
                "reason": str(e)
            })
            logger.error(
                f"Task failed for execution ID: {execution_id}, Reason: {str(e)}"
            )

    def submit_job(self, task_to_execute, job_payload: dict):
        """
        Submits a new task to be executed asynchronously. Generates a unique execution ID and tracks the job status.

        Args:
            task_to_execute (callable): The function to be executed asynchronously.
            job_payload (dict): The payload to pass to the task, excluding the execution ID.

        Returns:
            str: The unique execution ID of the submitted job.
        """
        execution_id = str(uuid.uuid4())
        job_payload["execution_id"] = execution_id
        self._update_status(execution_id, {"status": AsyncTaskStatus.QUEUED.value})
        logger.info(f"Job submitted with execution ID: {execution_id}")
        self.queue.submit(self.task_execute_wrapper, task_to_execute, job_payload)
        return execution_id

    def track_status(self, execution_id: str) -> dict:
        """
        Polls the current status of a task using its execution ID.

        Args:
            execution_id (str): The unique identifier for the task to track.

        Returns:
            dict: The current status of the task (QUEUED, STARTED, SUCCESS, FAILURE, or NA).
        """
        status = self._get_status(execution_id)
        logger.debug(
            f"Tracking status for task with execution ID: {execution_id}, Status: {status['status']}"
        )
        
        # Remove the execution_id from status tracker if task completed successfully
        if status["status"] == AsyncTaskStatus.SUCCESS.value:
            self._remove_status(execution_id)
            logger.debug(f"Removed execution ID {execution_id} from status tracker after status check")
        
        return status
