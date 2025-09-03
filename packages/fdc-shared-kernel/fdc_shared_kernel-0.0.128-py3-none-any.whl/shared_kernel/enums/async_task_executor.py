from enum import Enum


class AsyncTaskStatus(Enum):
    QUEUED = "Queued"
    STARTED = "Started"
    SUCCESS = "Success"
    FAILURE = "Failure"
    NA = "NA"
