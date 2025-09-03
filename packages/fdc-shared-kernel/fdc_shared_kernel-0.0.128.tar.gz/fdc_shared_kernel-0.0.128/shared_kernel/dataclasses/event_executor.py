"""
File: event_executor.py
Author: Akdham
Description: Dataclasses for event executor
Date: 2025-05-07
"""
from concurrent.futures import Future
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from shared_kernel.messaging.utils.event_messages import EventMessage

@dataclass
class EventStats:
    """Statistics for an event type"""
    successful_events: int = 0
    failed_events: int = 0
    
    @property
    def total_events(self) -> int:
        return self.successful_events + self.failed_events


@dataclass
class ActiveJob:
    """Represents a job currently being processed by the executor."""

    execution_future: Future
    event_msg_object: EventMessage
    track_id: Optional[int] = None  # use the span id to track the job


@dataclass
class EventContext:
    """Stores metadata and runtime statistics for an event."""

    schema: dict
    description: str
    callback: Callable[[Any], None]
    total_workers: int
    event_stats: EventStats
    active_jobs: List[ActiveJob] = field(default_factory=list)