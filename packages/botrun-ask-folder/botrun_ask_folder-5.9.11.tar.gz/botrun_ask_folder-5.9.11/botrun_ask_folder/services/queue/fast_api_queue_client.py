import aiohttp
import os
from typing import Union
from botrun_ask_folder.constants import FAST_API_TIMEOUT
from botrun_ask_folder.fast_api.util.http_request_retry_decorator import async_retry
from botrun_ask_folder.models.job_event import JobEvent
from botrun_ask_folder.services.queue.queue_client import QueueClient
from dotenv import load_dotenv

load_dotenv()

API_PREFIX = "api/botrun/botrun_ask_folder"
BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN = os.getenv("BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN")


class FastAPIQueueClient(QueueClient):
    def __init__(self, api_url: str = os.getenv("BOTRUN_ASK_FOLDER_FAST_API_URL")):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"}

    @async_retry(attempts=3, delay=1)
    async def enqueue(self, job: JobEvent) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/enqueue",
                json=job.model_dump(),
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["job_id"]

    @async_retry(attempts=3, delay=1)
    async def dequeue(self, all: bool = False) -> Union[JobEvent, None]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/queue/dequeue",
                params={"all": str(all).lower()},
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if "job" not in data:
                    return None
                return JobEvent(**data["job"])

    @async_retry(attempts=3, delay=1)
    async def complete_job(self, job_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/complete/{job_id}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()

    @async_retry(attempts=3, delay=1)
    async def fail_job(self, job_id: str, error: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/fail/{job_id}",
                json={"error": error},
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()

    @async_retry(attempts=3, delay=1)
    async def reset_job(self, job_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/reset/{job_id}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()

    @async_retry(attempts=3, delay=1)
    async def get_pending_job_count(self) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/queue/pending_count",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["pending_job_count"]

    @async_retry(attempts=3, delay=1)
    async def get_processing_job_count(self) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/queue/processing_count",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["processing_job_count"]
