from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import Dict, Union
from botrun_ask_folder.models.job_event import JobEvent
from botrun_ask_folder.services.queue.queue_store import QueueStore
from botrun_ask_folder.services.queue.queue_factory import queue_store_factory
from botrun_ask_folder.fast_api.jwt_util import verify_token

queue_api_router = APIRouter(prefix="/botrun_ask_folder", tags=["botrun_ask_folder"])


class QueueService:
    def __init__(self, queue_store: QueueStore):
        self.queue_store = queue_store

    async def enqueue(self, job: JobEvent) -> str:
        return await self.queue_store.enqueue(job)

    async def dequeue(self, all: bool = False) -> JobEvent:
        return await self.queue_store.dequeue(all)

    async def complete_job(self, job_id: str):
        await self.queue_store.complete_job(job_id)

    async def fail_job(self, job_id: str, error: str):
        await self.queue_store.fail_job(job_id, error)

    async def get_pending_job_count(self) -> int:
        return await self.queue_store.get_pending_job_count()

    async def get_processing_job_count(self) -> int:
        return await self.queue_store.get_processing_job_count()


service = QueueService(queue_store_factory())


@queue_api_router.post("/queue/enqueue", dependencies=[Depends(verify_token)])
async def enqueue_job(job: JobEvent = Body(...)) -> Dict[str, str]:
    try:
        job_id = await service.enqueue(job)
        return {"message": "Job enqueued successfully", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enqueuing job: {str(e)}")


@queue_api_router.get("/queue/dequeue", dependencies=[Depends(verify_token)])
async def dequeue_job(all: bool = Query(False)) -> Dict[str, Union[str, Dict]]:
    try:
        job = await service.dequeue(all)
        if job is None:
            return {"message": "No pending jobs available"}
        return {"message": "Job dequeued successfully", "job": job.model_dump()}
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error dequeuing job: {str(e)}")


@queue_api_router.post("/queue/complete/{job_id}", dependencies=[Depends(verify_token)])
async def complete_job(job_id: str) -> Dict[str, str]:
    try:
        await service.complete_job(job_id)
        return {"message": "Job completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing job: {str(e)}")


@queue_api_router.post("/queue/fail/{job_id}", dependencies=[Depends(verify_token)])
async def fail_job(job_id: str, error: str = Body(..., embed=True)) -> Dict[str, str]:
    try:
        await service.fail_job(job_id, error)
        return {"message": "Job marked as failed"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error marking job as failed: {str(e)}"
        )


@queue_api_router.post("/queue/reset/{job_id}", dependencies=[Depends(verify_token)])
async def reset_job(job_id: str) -> Dict[str, str]:
    try:
        await service.reset_job(job_id)
        return {"message": "Job reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting job: {str(e)}")


@queue_api_router.get("/queue/pending_count", dependencies=[Depends(verify_token)])
async def get_pending_job_count() -> Dict[str, int]:
    try:
        count = await service.get_pending_job_count()
        return {"pending_job_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting pending job count: {str(e)}"
        )


@queue_api_router.get("/queue/processing_count", dependencies=[Depends(verify_token)])
async def get_processing_job_count() -> Dict[str, int]:
    try:
        count = await service.get_processing_job_count()
        return {"processing_job_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting processing job count: {str(e)}"
        )
