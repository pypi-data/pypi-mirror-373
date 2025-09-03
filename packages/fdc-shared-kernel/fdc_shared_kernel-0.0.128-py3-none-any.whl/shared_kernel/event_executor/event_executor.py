from datetime import datetime
import threading
from concurrent.futures import Future
from typing import Any, Callable, Dict, Optional

from shared_kernel.config import Config
from shared_kernel.dataclasses.event_executor import ActiveJob, EventContext, EventStats
from shared_kernel.event_executor.job_executor import JobExecutor
from shared_kernel.event_executor.utils import EventConcurrencyManager
from shared_kernel.exceptions.http_exceptions import NotFound
from shared_kernel.interfaces import DataBus
from shared_kernel.logger import Logger
from shared_kernel.status_tracker import StatusTracker
from shared_kernel.traceability.traceability_handler import Traceability
from shared_kernel.utils.thread_local_storage import ThreadLocalStorage
from shared_kernel.messaging.utils.event_messages import EventMessage


app_config = Config()
logger = Logger(app_config.get("APP_NAME"))

thread_local_storage = ThreadLocalStorage()


class EventExecutor:
    _singleton_instance = None
    _singleton_lock = threading.Lock()

    def __new__(self, *args, **kwargs):
        with self._singleton_lock:
            if self._singleton_instance is None:
                instance = super().__new__(self)
                instance._is_initialized = False
                self._singleton_instance = instance
            return self._singleton_instance

    def __init__(
        self,
        databus: Optional[DataBus] = None,
        status_tracker: Optional[StatusTracker] = None,
    ):
        """Initialize the EventExecutor singleton.

        Args:
            databus (Optional[DataBus]): The DataBus instance to use for publishing messages.
            status_tracker (Optional[StatusTracker]): The StatusTracker instance to use for tracking status.
        """
        with self._singleton_lock:
            if self._is_initialized:
                return

            # checked only during initial initialization - that is during app startup
            if databus is None or status_tracker is None:
                raise ValueError(
                    "DataBus and StatusTracker must be provided for initial initialization"
                )

            # initialize core components
            self.databus = databus
            self.status_tracker = status_tracker
            self.job_executor = JobExecutor(status_tracker, databus)
            self._event_listener_threads: Dict[str, threading.Thread] = {}
            self._event_concurrency_manager = EventConcurrencyManager()
            self._shutdown_flag = threading.Event()
            self._event_catalog: Dict[str, EventContext] = {}

            self._is_initialized = True
            logger.info("EventExecutor singleton initialized.")

    def get_stats(self, event_name: str) -> EventStats:
        """Return statistics for a specific event."""
        if event_name in self._event_catalog:
            return self._event_catalog[event_name].event_stats
        return EventStats()

    def _on_job_execution_complete(
        self,
        execution_future: Future,
        event_name: str,
        event_semaphore: threading.Semaphore,
        active_job: ActiveJob,
    ) -> None:
        """
        Callback executed after a job completes. Updates counters and releases semaphore.

        Args:
            execution_future (Future): the completed future
            event_name (str): name of the event
            event_semaphore (Semaphore): semaphore controlling concurrency
            active_job (ActiveJob): the job object containing the future and payload
        """
        try:
            if active_job in self._event_catalog[event_name].active_jobs:
                self._event_catalog[event_name].active_jobs.remove(active_job)

            try:
                execution_future.result()  # will raise if the job failed
                self._event_catalog[event_name].event_stats.successful_events += 1
            except Exception:
                self._event_catalog[event_name].event_stats.failed_events += 1
        finally:
            # always release the semaphore, even if there's an exception
            event_semaphore.release()

    def _listen_events(self, event_name: str) -> None:
        """Listen to the async event source and dispatch jobs."""
        logger.info(f"Starting event listener for [{event_name}].")

        event_semaphore = self._event_concurrency_manager.get_event_semaphore(
            event_name=event_name
        )
        event_threadpool_executor = (
            self._event_concurrency_manager.get_event_threadpool_executor(
                event_name=event_name
            )
        )
        event_context = self._event_catalog[event_name]

        while not self._shutdown_flag.is_set():
            is_semaphore_acquired = False
            try:
                is_semaphore_acquired = event_semaphore.acquire(timeout=0.5)
                if is_semaphore_acquired:
                    # get message from the databus
                    event_msg_object: EventMessage = self.databus.get_message(event_name)
                    if event_msg_object:
                        logger.info(
                            f"Received message for event {event_name}: {event_msg_object.raw_message}"
                        )
                        
                        # update the start time for the received event and update trace in processing
                        trace_id = event_msg_object.event_meta.trace_id
                        if trace_id:
                            tracebility_handler = Traceability(trace_id)
                            try:
                                response = tracebility_handler.update({
                                    "execution_status": "Processing"
                                })
                                logger.info(
                                    f"Marking the trace id {trace_id} as processing {response}")
                            except NotFound as e:
                                logger.info("Trace Id Not found. Skip the status update")
                        # submit job to executor
                        execution_future = event_threadpool_executor.submit(
                            self.job_executor.submit_job,
                            event_context.callback,
                            event_msg_object,
                        )

                        # Create active job with thread reference
                        active_job = ActiveJob(
                            execution_future=execution_future,
                            event_msg_object=event_msg_object,
                            # Store track id to track the observability under an event
                            track_id=event_msg_object.raw_message["event_meta"]["span_id"]
                        )
                        self._event_catalog[event_name].active_jobs.append(active_job)

                        # assign callback to future
                        execution_future.add_done_callback(
                            lambda fut, event_name=event_name, event_semaphore=event_semaphore, active_job=active_job: self._on_job_execution_complete(
                                fut, event_name, event_semaphore, active_job
                            )
                        )

                        # we don't release the semaphore here because it will be released in _task_done_callback
                        is_semaphore_acquired = False
                    else:
                        # no message, release semaphore to permit
                        event_semaphore.release()
                        is_semaphore_acquired = False
                else:
                    # if we couldn't acquire the semaphore, wait for 0.1 seconds
                    self._shutdown_flag.wait(0.1)
            except Exception as e:
                logger.error(f"Error in event listener for {event_name}: {str(e)}")
                # TODO: implement retry logic or circuit breaker pattern here - needs to do some research on this
            finally:
                # make sure semaphore is released if we encountered an exception after acquiring it
                if is_semaphore_acquired:
                    event_semaphore.release()

        logger.info(f"Event listener for {event_name} has been stopped.")

    def get_event_catalog(self) -> dict:
        """Return the event catalog."""
        return self._event_catalog

    def get_databus_instance(self) -> DataBus:
        """Return the databus instance"""
        return self.databus

    def register_event(
        self,
        event_name: str,
        event_schema: dict,
        event_description: str,
        callback: Callable[[Any], None],
        max_concurrency: int,
    ) -> dict:
        """Register an event and start listening for messages."""
        with self._singleton_lock:  # protect against concurrent register_event calls
            if event_name in self._event_listener_threads:
                raise ValueError(f"Event {event_name} is already registered")

            # register with async bus and set up concurrency controls
            self.databus.subscribe_async_event(event_name, None)
            self._event_concurrency_manager.set_event_concurrency(
                event_name=event_name, max_concurrency=max_concurrency
            )

            # initialize with default EventStats
            self._event_catalog[event_name] = EventContext(
                schema=event_schema,
                description=event_description,
                callback=callback,
                total_workers=max_concurrency,
                event_stats=EventStats(),
            )

            # launch listener thread
            long_running_event_listener_thread = threading.Thread(
                target=self._listen_events,
                args=(event_name,),
                name=f"EventListener-{event_name}",
                daemon=True,
            )
            self._event_listener_threads[event_name] = long_running_event_listener_thread
            long_running_event_listener_thread.start()
            logger.info(f"Event {event_name} registered and listener started.")

            return True

    def shutdown(self) -> None:
        """Shut down all running threads and cleanup resources."""
        self._shutdown_flag.set()

        for event_name, thread in self._event_listener_threads.items():
            logger.info(f"Shutting down thread for event {event_name}")
            thread.join(timeout=30)  # Don't wait forever

            if thread.is_alive():
                logger.warning(
                    f"Thread for event {event_name} did not terminate gracefully"
                )

        # wait for all running jobs to finish with timeout
        for event_name, catalog in self._event_catalog.items():
            for job in catalog.active_jobs:
                try:
                    # Set a timeout to avoid hanging
                    job.execution_future.result(timeout=10)
                except Exception as e:
                    logger.error(
                        f"Error during shutdown of task for event {event_name}: {str(e)}"
                    )

        # shut down executors
        for (
            event_name,
            executor,
        ) in self._event_concurrency_manager.event_threadpool_executors.items():
            logger.info(f"Shutting down executor for event {event_name}")
            executor.shutdown(wait=True)

        self._event_listener_threads.clear()
        self._event_concurrency_manager.event_threadpool_executors.clear()
        self._event_concurrency_manager.event_semaphores.clear()
        logger.info("EventExecutor shutdown complete.")
