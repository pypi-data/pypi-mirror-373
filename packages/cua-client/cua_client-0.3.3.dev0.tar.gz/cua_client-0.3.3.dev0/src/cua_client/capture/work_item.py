from dataclasses import dataclass

__all__ = ["WorkItem"]


@dataclass
class WorkItem:
    """Payload object passed from ImageBatchRecorder to the sender thread."""

    session_id: int
    batch_id: int
    images_zip: bytes
    key_logs: str
    attempt: int = 0 