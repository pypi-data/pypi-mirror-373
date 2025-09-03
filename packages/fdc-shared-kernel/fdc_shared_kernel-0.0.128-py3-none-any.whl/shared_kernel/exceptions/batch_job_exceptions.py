class BatchJobFailedException(Exception):
    """
    Raised when an AWS Batch job fails, optionally with details extracted
    from job logs or result files.
    """
    def __init__(self, job_type: str, reason: str = "Unknown error occurred in Batch job", job_name: str = None, job_id: str = None):
        self.job_id = job_id
        self.job_name = job_name
        self.job_type = job_type
        self.reason = reason
        parts = [f"{job_type} batch job failed"]

        if job_name:
            parts.append(f"(Job Name: {job_name})")
        if job_id:
            parts.append(f"(Job ID: {job_id})")

        parts.append(f"Reason: {reason}")
        message = " | ".join(parts)

        super().__init__(message)
