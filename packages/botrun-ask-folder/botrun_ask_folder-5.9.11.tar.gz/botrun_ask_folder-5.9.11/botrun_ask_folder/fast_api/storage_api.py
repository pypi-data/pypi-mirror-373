from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from fastapi.responses import StreamingResponse
from typing import Dict
from io import BytesIO
from urllib.parse import unquote

from botrun_ask_folder.services.storage.storage_store import StorageStore
from botrun_ask_folder.services.storage.storage_factory import storage_store_factory
from botrun_ask_folder.fast_api.jwt_util import verify_token

storage_api_router = APIRouter(prefix="/botrun_ask_folder", tags=["botrun_ask_folder"])


class StorageService:
    def __init__(self, storage_store: StorageStore):
        self.storage_store = storage_store

    async def store_file(self, filepath: str, file_object: BytesIO) -> bool:
        return await self.storage_store.store_file(filepath, file_object)

    async def retrieve_file(self, filepath: str) -> BytesIO:
        return await self.storage_store.retrieve_file(filepath)

    async def delete_file(self, filepath: str) -> bool:
        return await self.storage_store.delete_file(filepath)

    async def file_exists(self, filepath: str) -> bool:
        return await self.storage_store.file_exists(filepath)


service = StorageService(storage_store_factory())


@storage_api_router.post("/storage", dependencies=[Depends(verify_token)])
async def store_file(file: UploadFile = File(...), filepath: str = Query(None)):
    if filepath:
        filepath = unquote(filepath)
    print(f"Uploading file: {file.filename} to path: {filepath}")
    if filepath is None:
        filepath = file.filename

    print(f"waiting for file content")
    file_content = await file.read()
    print("file content ready")
    file_object = BytesIO(file_content)
    print("file object ready")

    try:
        print("storing file")
        success = await service.store_file(filepath, file_object)
        if success:
            print("file stored")
            return {"message": "File uploaded successfully", "filepath": filepath}
        else:
            print("file not stored")
            raise HTTPException(status_code=500, detail="Failed to upload file")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@storage_api_router.get(
    "/storage/{filepath:path}", dependencies=[Depends(verify_token)]
)
async def download_file(filepath: str):
    try:
        file_object = await service.retrieve_file(filepath)
        if file_object is None:
            raise HTTPException(status_code=404, detail="File not found")

        return StreamingResponse(
            file_object,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filepath.split('/')[-1]}"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@storage_api_router.delete(
    "/storage/{filepath:path}", dependencies=[Depends(verify_token)]
)
async def delete_file(filepath: str) -> Dict[str, str]:
    try:
        if not await service.file_exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        success = await service.delete_file(filepath)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@storage_api_router.get(
    "/storage/{filepath:path}/exists", dependencies=[Depends(verify_token)]
)
async def check_file_exists(filepath: str) -> Dict[str, bool]:
    try:
        exists = await service.file_exists(filepath)
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error checking file existence: {str(e)}"
        )
