from abc import ABC, abstractmethod
from botrun_ask_folder.models.job_event import JobEvent


class QueueClient(ABC):
    @abstractmethod
    async def enqueue(self, job: JobEvent) -> str:
        pass

    @abstractmethod
    async def dequeue(self, all: bool = False) -> JobEvent:
        pass

    @abstractmethod
    async def complete_job(self, job_id: str):
        pass

    @abstractmethod
    async def fail_job(self, job_id: str, error: str):
        pass

    @abstractmethod
    async def reset_job(self, job_id: str):
        pass

    @abstractmethod
    async def get_pending_job_count(self) -> int:
        pass

    @abstractmethod
    async def get_processing_job_count(self) -> int:
        pass
