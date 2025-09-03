"""
File name: job_status_mapper.py
 * Last upadted: 21/07/2025
 * Author: Sanjeev Shaji
 * Last Change: BI-2135 - Added AWS Batch job handling modules to shared_kernel
"""

from shared_kernel.enums.status_tracker import TaskStatus

# Maps AWS job statuses to internal task statuses
JOB_STATUS_TO_TASK_STATUS = {
            "SUBMITTED": TaskStatus.QUEUED,
            "PENDING": TaskStatus.QUEUED,
            "RUNNABLE": TaskStatus.QUEUED,
            "STARTING": TaskStatus.PROCESSING,
            "RUNNING": TaskStatus.PROCESSING,
            "SUCCEEDED": TaskStatus.COMPLETED,
            "FAILED": TaskStatus.FAILURE,
        }