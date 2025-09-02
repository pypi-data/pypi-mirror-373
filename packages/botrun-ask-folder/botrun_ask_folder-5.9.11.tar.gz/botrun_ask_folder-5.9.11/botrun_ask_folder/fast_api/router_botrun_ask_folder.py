from typing import Optional
from fastapi import FastAPI, HTTPException, Query, APIRouter, Depends
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import io
import os
import json
import asyncio
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from botrun_ask_folder.constants import TOPIC_USER_INPUT_FOLDER
from botrun_ask_folder.embeddings_to_qdrant import embeddings_to_qdrant_distributed

from botrun_ask_folder.fast_api.util.pdf_util import pdf_page_to_image, DEFAULT_DPI
from botrun_ask_folder.google_drive_service import get_google_drive_service
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.drive_folder import DriveFolder, DriveFolderStatus
from botrun_ask_folder.models.splitted_file import SplittedFile, SplittedFileStatus

from botrun_ask_folder.services.drive.drive_factory import (
    drive_client_factory,
)
from botrun_ask_folder.services.queue.queue_factory import (
    queue_client_factory,
)
from botrun_ask_folder.models.job_event import JobEvent, JobStatus, JobType
from google.cloud import run_v2
from google.cloud.run_v2.types import RunJobRequest
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import pytz
from botrun_ask_folder.fast_api.jwt_util import verify_token
from botrun_ask_folder.util.timestamp_encryp import decrypt_timestamp

load_dotenv()

# Create 'dev' directory in the current working directory
dev_dir = "./dev"
os.makedirs(dev_dir, exist_ok=True)

router = APIRouter(prefix="/botrun_ask_folder", tags=["botrun_ask_folder"])


current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
router.mount("/static", StaticFiles(directory=static_dir), name="static")


def validate_dev_token(
    token: str = Query(..., description="Development token for authentication")
):
    dev_token = os.getenv("DEV_TOKEN")
    if not dev_token or token != dev_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    return token


@router.get("/dev/kb")
async def get_kb(token: str = Depends(validate_dev_token)):
    try:
        return FileResponse(os.path.join(dev_dir, "kb.txt"))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="KB file not found")


@router.get("/dev/keyword")
async def get_keyword(token: str = Depends(validate_dev_token)):
    try:
        return FileResponse(os.path.join(dev_dir, "keyword.txt"))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Keyword file not found")


@router.get("/stress", response_class=FileResponse)
async def stress_page():
    return FileResponse(os.path.join(static_dir, "stress.html"))


@router.get("/folder_status_web", response_class=FileResponse)
async def folder_status_web():
    return FileResponse(os.path.join(static_dir, "folder_status.html"))


@router.get("/folder_status_web_en", response_class=FileResponse)
async def folder_status_web_en():
    return FileResponse(os.path.join(static_dir, "folder_status_en.html"))


@router.get("/download_file/{file_id}")
def download_file(file_id: str):
    service_account_file = "keys/google_service_account_key.json"
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=credentials)

    try:
        file = (
            drive_service.files().get(fileId=file_id, fields="name, mimeType").execute()
        )
        file_name = file.get("name")
        file_mime_type = file.get("mimeType")

        request = drive_service.files().get_media(fileId=file_id)

        def file_stream():
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                yield fh.getvalue()
                fh.seek(0)
                fh.truncate(0)

        # Encode the filename for Content-Disposition
        encoded_filename = quote(file_name)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Content-Type": file_mime_type,
        }

        return StreamingResponse(
            file_stream(), headers=headers, media_type=file_mime_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_pdf_page/{file_id}")
def get_pdf_page(
    file_id: str,
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    dpi: int = Query(DEFAULT_DPI, ge=72, le=600, description="DPI for rendering"),
    scale: float = Query(1.0, ge=0.1, le=2.0, description="Scaling factor"),
    color: bool = Query(True, description="Render in color if True, else grayscale"),
):
    try:
        img_byte_arr = pdf_page_to_image(
            file_id=file_id, page=page, dpi=dpi, scale=scale, color=color
        )

        return Response(content=img_byte_arr, media_type="image/png")
    except ValueError as e:
        return Response(content=str(e), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FolderRequest(BaseModel):
    folder_id: str
    force: bool = False
    embed: bool = True
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""
    qdrant_prefix: Optional[str] = None
    qdrant_https: bool = False


@router.post("/process-folder-job", dependencies=[Depends(verify_token)])
async def process_folder_job(request: FolderRequest):
    print(
        f"Processing folder {request.folder_id} with force={request.force} using Cloud Run Job"
    )
    queue_client = queue_client_factory()
    await queue_client.enqueue(
        JobEvent(
            job_type=JobType.LIST_FILES,
            status=JobStatus.PENDING,
            data=json.dumps(
                {
                    "folder_id": request.folder_id,
                    "force": request.force,
                    "qdrant_host": request.qdrant_host,
                    "qdrant_port": request.qdrant_port,
                    "qdrant_api_key": request.qdrant_api_key,
                    "qdrant_prefix": request.qdrant_prefix,
                    "qdrant_https": request.qdrant_https,
                },
            ),
        )
    )

    # Get the credentials from the key file
    google_service_account_key_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
        "/app/keys/scoop-386004-d22d99a7afd9.json",
    )
    credentials = service_account.Credentials.from_service_account_file(
        google_service_account_key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    # Create a Cloud Run Jobs client
    client = run_v2.JobsClient(credentials=credentials)

    # Get the project ID from the credentials
    project = credentials.project_id

    # Prepare the job request
    job_name = f"projects/{project}/locations/{os.getenv('CLOUD_RUN_REGION', 'asia-east1')}/jobs/process-folder-job"

    # args = [
    #     "--folder_id",
    #     request.folder_id,
    #     "--qdrant_host",
    #     request.qdrant_host,
    #     "--qdrant_port",
    #     str(request.qdrant_port),
    #     "--qdrant_api_key",
    #     request.qdrant_api_key,
    # ]
    # if request.force:
    #     args.append("--force")
    # if not request.embed:
    #     args.append("--no-embed")
    container_override = RunJobRequest.Overrides.ContainerOverride(
        name="asia-east1-docker.pkg.dev/scoop-386004/botrun-ask-folder/botrun-ask-folder-job",
        # args=args,
    )

    job_overrides = RunJobRequest.Overrides(container_overrides=[container_override])

    job_request = RunJobRequest(name=job_name, overrides=job_overrides)

    print(
        "start invoke Cloud Run Job process_folder_job with folder_id: ",
        request.folder_id,
    )
    # 触发 Job
    try:
        operation = client.run_job(request=job_request)
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error in process_folder_job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    # 返回成功响应
    return {
        "message": "Job triggered successfully",
        "job_id": operation.metadata.name,
        "status": "success",
    }


class FolderStatusEncRequest(BaseModel):
    folder_id: str
    enc_data: str
    include_file_status: bool = False


@router.post("/folder-status-enc")
async def folder_status_enc(request: FolderStatusEncRequest):
    try:
        # Get the encryption key from environment variable
        key = os.getenv("FOLDER_STATUS_ENC_KEY")
        if not key:
            raise HTTPException(status_code=500, detail="Encryption key not found")

        # Decrypt the enc_data
        try:
            decrypted_timestamp = decrypt_timestamp(request.enc_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        taipei_tz = pytz.timezone("Asia/Taipei")
        # Check if the timestamp is within a reasonable range (e.g., last 1 day)
        if datetime.now(taipei_tz) - decrypted_timestamp > timedelta(days=1):
            raise HTTPException(status_code=400, detail="Timestamp expired")

        # If everything is valid, call the original folder_status function
        folder_status_request = FolderStatusRequest(
            folder_id=request.folder_id,
            action_started_at=decrypted_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            include_file_status=request.include_file_status,
        )
        return await folder_status(folder_status_request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FolderStatusRequest(BaseModel):
    folder_id: str
    # 因為 cloud run job 沒有立即執行，所以加入這個參數，如果偵測到 folder updated_at 比 action_started_at 舊，就回等待中
    action_started_at: str = ""
    include_file_status: bool = False


@router.post("/folder-status", dependencies=[Depends(verify_token)])
async def folder_status(request: FolderStatusRequest):
    folder_id = request.folder_id
    client = drive_client_factory()

    try:
        folder = await client.get_drive_folder(folder_id)
        if folder is None:
            return {
                "status": "WAITING",
                "message": f"Folder {folder_id} not found, Folder is waiting to be processed",
            }
        if request.action_started_at and folder.updated_at < request.action_started_at:
            return {
                "status": "WAITING",
                "message": "Folder is waiting to be processed",
            }
        total_files = len(folder.items)
        embedded_files_count = 0
        not_embedded_files = []
        if request.include_file_status:
            for file_id in folder.items:
                drive_file = await client.get_drive_file(file_id)
                if drive_file.status == DriveFileStatus.EMBEDDED:
                    embedded_files_count += 1
                else:
                    not_embedded_files.append(file_id)

        # embedded_files = sum(
        #     1
        #     for status in folder.file_statuses.values()
        #     if status == DriveFileStatus.EMBEDDED
        # )

        response = {
            "status": folder.status.value,
            "message": f"Folder {folder_id} status: {folder.status.value}",
            "updated_at": folder.updated_at,
            "total_files": total_files,
            "include_file_status": request.include_file_status,
            "embedded_files_count": embedded_files_count,
            "not_embedded_files": not_embedded_files,
            "last_update_items_timestamp": folder.last_update_items_timestamp,
            "last_update_items": folder.last_update_items,
            "last_update_failed_items": folder.last_update_failed_items,
        }

        if folder.status == DriveFolderStatus.DONE:
            response["message"] = f"Folder {folder_id} processing completed"
        elif folder.status == DriveFolderStatus.INTIATED:
            response["message"] = f"Folder {folder_id} processing not started yet"
        elif folder.status == DriveFolderStatus.PROCESSING:
            response["message"] = f"Folder {folder_id} is being processed"

        print(f"[Folder {folder_id}] Response: {response}")
        return response

    except Exception as e:
        print(f"[Folder {folder_id}] Error in folder_status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing folder status: {str(e)}"
        )


@router.post("/complete-all-jobs", dependencies=[Depends(verify_token)])
async def complete_all_jobs():
    """
    清空所有 job queue 裡的 job，開發用
    """
    queue_client = queue_client_factory()
    completed_count = 0

    try:
        while True:
            job = await queue_client.dequeue(all=True)
            if job is None:
                break

            if hasattr(job, "id"):
                await queue_client.complete_job(job.id)
                completed_count += 1

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error completing jobs: {str(e)}")

    return {
        "message": "All jobs completed",
        "status": "success",
        "jobs_completed": completed_count,
    }


class FolderLastUpdateRequest(BaseModel):
    folder_id: str


@router.post("/folder-last-update-items", dependencies=[Depends(verify_token)])
async def folder_last_update_items(request: FolderLastUpdateRequest):
    folder_id = request.folder_id
    client = drive_client_factory()

    try:
        folder = await client.get_drive_folder(folder_id)
        if folder is None:
            return {
                "status": "NOT_FOUND",
                "message": f"Folder {folder_id} not found",
            }

        response = {
            "status": "SUCCESS",
            "message": f"Last update items for folder {folder_id}",
            "last_update_items_timestamp": folder.last_update_items_timestamp,
            "last_update_items": folder.last_update_items,
        }

        print(f"[Folder {folder_id}] Last Update Items Response: {response}")
        return response

    except Exception as e:
        print(f"[Folder {folder_id}] Error in folder_last_update_items: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing folder last update items: {str(e)}",
        )


# 添加新的請求模型
class FileStatusRequest(BaseModel):
    file_id: str


# 添加新的端點
@router.post("/file-status", dependencies=[Depends(verify_token)])
async def file_status(request: FileStatusRequest):
    file_id = request.file_id
    client = drive_client_factory()

    try:
        drive_file = await client.get_drive_file(file_id)
        if drive_file is None:
            return {
                "status": "NOT_FOUND",
                "message": f"File {file_id} not found",
            }

        response = {
            "status": "SUCCESS",
            "message": f"Status for file {file_id}",
            "file_status": drive_file.status.value,
            "file_name": drive_file.name,
            "updated_at": drive_file.updated_at,
            "folder_id": drive_file.folder_id,
            "mime_type": drive_file.mimeType,
            "modified_time": drive_file.modifiedTime,
            "size": drive_file.size,
        }

        print(f"[File {file_id}] File Status Response: {response}")
        return response

    except Exception as e:
        print(f"[File {file_id}] Error in file_status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file status: {str(e)}",
        )
