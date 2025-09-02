from google.cloud import firestore
from google.cloud.firestore import FieldFilter
from google.oauth2 import service_account
import os
from datetime import datetime
import pytz
from botrun_ask_folder.models.job_event import JobEvent, JobStatus
from botrun_ask_folder.services.queue.queue_store import (
    QueueStore,
    QUEUE_STORE_NAME,
)
from google.cloud.firestore_v1.transaction import Transaction


class QueueFsStore(QueueStore):
    def __init__(self):
        google_service_account_key_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
            "/app/keys/scoop-386004-d22d99a7afd9.json",
        )
        credentials = service_account.Credentials.from_service_account_file(
            google_service_account_key_path,
            scopes=["https://www.googleapis.com/auth/datastore"],
        )

        self.db = firestore.Client(credentials=credentials)
        self.collection = self.db.collection(QUEUE_STORE_NAME)

    async def enqueue(self, job: JobEvent) -> str:
        doc_ref = self.collection.document(job.id)
        doc_ref.set(job.model_dump())
        return job.id

    async def dequeue(self, all: bool = False) -> JobEvent:
        @firestore.transactional
        def dequeue_transaction(transaction, all: bool = False):
            if all:
                query = self.collection.order_by("updated_at").limit(1)
            else:
                query = (
                    self.collection.where(
                        filter=FieldFilter("status", "==", JobStatus.PENDING.value)
                    )
                    .order_by("updated_at")
                    .limit(1)
                )
            docs = list(query.stream(transaction=transaction))

            if not docs:
                return None

            doc = docs[0]
            doc_ref = doc.reference

            job_data = doc.to_dict()
            job = JobEvent(**job_data)
            job.status = JobStatus.PROCESSING
            job.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            transaction.update(doc_ref, job.model_dump())

            return job

        transaction = self.db.transaction()
        return dequeue_transaction(transaction, all)

    async def complete_job(self, job_id, transaction=None):
        doc_ref = self.collection.document(job_id)
        doc_ref.delete()

    async def fail_job(self, job_id: str, error: str):
        doc_ref = self.collection.document(job_id)
        job_data = doc_ref.get().to_dict()
        job = JobEvent(**job_data)
        job.status = JobStatus.FAILED
        job.error = error
        job.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        await doc_ref.update(job.model_dump())

    async def reset_job(self, job_id: str):
        doc_ref = self.collection.document(job_id)
        job_data = doc_ref.get().to_dict()
        job = JobEvent(**job_data)
        job.status = JobStatus.PENDING
        job.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        await doc_ref.update(job.model_dump())

    async def get_pending_job_count(self) -> int:
        query = self.collection.where(
            filter=FieldFilter("status", "==", JobStatus.PENDING.value)
        )
        # 使用 count() 方法直接获取文档数量
        return query.count().get()[0][0].value

    async def get_processing_job_count(self) -> int:
        query = self.collection.where(
            filter=FieldFilter("status", "==", JobStatus.PROCESSING.value)
        )
        return query.count().get()[0][0].value
