from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Semaphore
from typing import Dict

class EventConcurrencyManager:
    def __init__(self) -> None:
        self.event_threadpool_executors: Dict[str, ThreadPoolExecutor] = {}
        self.event_semaphores: Dict[str, Semaphore] = {}

    def set_event_concurrency(self, event_name: str, max_concurrency: int):
        # defining executor with max workers for an event
        executor = ThreadPoolExecutor(
            max_workers=max_concurrency, thread_name_prefix=f"Executor-{event_name}"
        )
        self.event_threadpool_executors[event_name] = executor

        # defining a semaphore with max workers
        semaphore = Semaphore(int(max_concurrency))
        self.event_semaphores[event_name] = semaphore

    def get_event_threadpool_executor(self, event_name: str):
        executor = self.event_threadpool_executors.get(event_name)
        return executor

    def get_event_semaphore(self, event_name: str):
        semaphore = self.event_semaphores.get(event_name)
        return semaphore