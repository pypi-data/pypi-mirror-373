from fastapi import FastAPI, HTTPException, Query, APIRouter, Body
from typing import Dict, List, Union
from pydantic import BaseModel

from openai import BaseModel
from botrun_ask_folder.models.drive_folder import DriveFolder
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.splitted_file import SplittedFile
from botrun_ask_folder.services.drive.drive_store import (
    DriveFolderStore,
    DriveFileStore,
    SplittedFileStore,
)

from botrun_ask_folder.services.drive.drive_factory import (
    drive_folder_store_factory,
    drive_file_store_factory,
    splitted_file_store_factory,
)

drive_api_router = APIRouter(prefix="/botrun_ask_folder", tags=["botrun_ask_folder"])


class DriveService:
    def __init__(
        self,
        folder_store: DriveFolderStore,
        file_store: DriveFileStore,
        splitted_file_store: SplittedFileStore,
    ):
        self.folder_store = folder_store
        self.file_store = file_store
        self.splitted_file_store = splitted_file_store

    async def get_drive_folder(self, folder_id: str) -> Union[DriveFolder, None]:
        return await self.folder_store.get_drive_folder(folder_id)

    async def set_drive_folder(self, folder: DriveFolder):
        await self.folder_store.set_drive_folder(folder)

    async def delete_drive_folder(self, folder_id: str):
        await self.folder_store.delete_drive_folder(folder_id)

    # async def update_drive_file_status_in_folder(
    #     self, folder_id: str, file_id: str, new_status: DriveFileStatus
    # ):
    #     await self.folder_store.update_drive_file_status_in_folder(
    #         folder_id, file_id, new_status
    #     )

    async def get_drive_file(self, file_id: str) -> Union[DriveFile, None]:
        return await self.file_store.get_drive_file(file_id)

    async def set_drive_file(self, file: DriveFile):
        await self.file_store.set_drive_file(file)

    async def delete_drive_file(self, file_id: str):
        await self.file_store.delete_drive_file(file_id)

    async def get_splitted_file(self, file_id: str) -> Union[SplittedFile, None]:
        return await self.splitted_file_store.get_splitted_file(file_id)

    async def set_splitted_file(self, file: SplittedFile):
        await self.splitted_file_store.set_splitted_file(file)

    async def delete_splitted_file(self, file_id: str):
        await self.splitted_file_store.delete_splitted_file(file_id)

    async def get_non_embedded_files_count(
        self, file_ids: List[str], batch_size: int = 30
    ) -> int:
        print(f"[drive_service][get_non_embedded_files_count] file_ids: {file_ids}")
        return await self.file_store.get_non_embedded_files_count(file_ids, batch_size)


service = DriveService(
    drive_folder_store_factory(),
    drive_file_store_factory(),
    splitted_file_store_factory(),
)


# Drive Folder endpoints
@drive_api_router.post("/drive_folder")
async def set_drive_folder(drive_folder: DriveFolder = Body(...)):
    try:
        await service.set_drive_folder(drive_folder)
        return {
            "message": "Drive folder initialized successfully",
            "drive_folder": drive_folder,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error initializing drive_folder: {str(e)}"
        )


@drive_api_router.get("/drive_folder/{folder_id}")
async def get_drive_folder(folder_id: str) -> DriveFolder:
    try:
        drive_folder = await service.get_drive_folder(folder_id)
        if drive_folder is None:
            raise HTTPException(status_code=404, detail="Drive folder not found")
        return drive_folder
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving drive folder: {str(e)}"
        )


@drive_api_router.delete("/drive_folder/{folder_id}")
async def delete_drive_folder(folder_id: str) -> Dict[str, str]:
    try:
        await service.delete_drive_folder(folder_id)
        return {"message": "Drive folder deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting drive folder: {str(e)}"
        )


# class UpdateFileStatusRequest(BaseModel):
#     file_id: str
#     new_status: DriveFileStatus


# @drive_api_router.post("/drive_folder/{folder_id}/update_file_status")
# async def update_drive_file_status(folder_id: str, request: UpdateFileStatusRequest):
#     try:
#         await service.update_drive_file_status_in_folder(
#             folder_id, request.file_id, request.new_status
#         )
#         return {"message": "Drive file status updated successfully"}
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error updating drive file status: {str(e)}"
#         )


# Drive File endpoints
@drive_api_router.post("/drive_file")
async def set_drive_file(drive_file: DriveFile = Body(...)):
    try:
        await service.set_drive_file(drive_file)
        return {
            "message": "Drive file initialized successfully",
            "drive_file": drive_file,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error initializing drive_file: {str(e)}"
        )


@drive_api_router.get("/drive_file/{file_id}")
async def get_drive_file(file_id: str) -> DriveFile:
    try:
        drive_file = await service.get_drive_file(file_id)
        if drive_file is None:
            raise HTTPException(status_code=404, detail="Drive file not found")
        return drive_file
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving drive file: {str(e)}"
        )


@drive_api_router.delete("/drive_file/{file_id}")
async def delete_drive_file(file_id: str) -> Dict[str, str]:
    try:
        await service.delete_drive_file(file_id)
        return {"message": "Drive file deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting drive file: {str(e)}"
        )


# Splitted File endpoints
@drive_api_router.post("/splitted_file")
async def set_splitted_file(splitted_file: SplittedFile = Body(...)):
    try:
        await service.set_splitted_file(splitted_file)
        return {
            "message": "Splitted file initialized successfully",
            "splitted_file": splitted_file,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error initializing splitted_file: {str(e)}"
        )


@drive_api_router.get("/splitted_file/{file_id}")
async def get_splitted_file(file_id: str) -> SplittedFile:
    try:
        splitted_file = await service.get_splitted_file(file_id)
        if splitted_file is None:
            raise HTTPException(status_code=404, detail="Splitted file not found")
        return splitted_file
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving splitted file: {str(e)}"
        )


@drive_api_router.delete("/splitted_file/{file_id}")
async def delete_splitted_file(file_id: str) -> Dict[str, str]:
    try:
        await service.delete_splitted_file(file_id)
        return {"message": "Splitted file deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting splitted file: {str(e)}"
        )


@drive_api_router.post("/drive_folder/{folder_id}/update_files")
async def update_drive_files(folder_id: str, new_files: List[DriveFile] = Body(...)):
    try:
        folder = await service.get_drive_folder(folder_id)
        if folder is None:
            raise HTTPException(status_code=404, detail="Drive folder not found")

        # Get the existing file IDs in the folder
        existing_file_ids = set(folder.items)

        # Find new files that are not already in the folder
        new_file_ids = [
            file.id for file in new_files if file.id not in existing_file_ids
        ]

        # Update DriveFolder items only if there are new files
        if new_file_ids:
            folder.items.extend(new_file_ids)
            await service.set_drive_folder(folder)

        # Update or add DriveFiles
        for file in new_files:
            await service.set_drive_file(file)

        return {
            "message": "Drive folder and files updated successfully",
            "new_files_added": len(new_file_ids),
            "total_files": len(folder.items),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating drive files: {str(e)}"
        )


@drive_api_router.get("/drive_folder/{folder_id}/split_files")
async def get_split_files(folder_id: str):
    try:
        folder = await service.get_drive_folder(folder_id)
        if folder is None:
            raise HTTPException(status_code=404, detail="Drive folder not found")

        split_files = {}
        for file_id in folder.items:
            drive_file = await service.get_drive_file(file_id)
            for split_file_id in drive_file.splitted_files:
                split_file = await service.get_splitted_file(split_file_id)
                split_files[split_file.name] = split_file

        return split_files
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving split files: {str(e)}"
        )


@drive_api_router.get("/drive_folder/{folder_id}/files")
async def get_drive_files(folder_id: str) -> List[DriveFile]:
    try:
        folder = await service.get_drive_folder(folder_id)
        if folder is None:
            raise HTTPException(status_code=404, detail="Drive folder not found")

        drive_files = []
        for file_id in folder.items:
            drive_file = await service.get_drive_file(file_id)
            if drive_file is not None:
                drive_files.append(drive_file)

        return drive_files
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving drive files: {str(e)}"
        )


# 新增一個 Pydantic 模型來定義請求體的結構
class NonEmbeddedFilesCountRequest(BaseModel):
    file_ids: List[str]
    batch_size: int = 1000  # 設置默認值為 1000


@drive_api_router.post("/drive_files/non_embedded_count")
async def get_non_embedded_files_count(
    request: NonEmbeddedFilesCountRequest = Body(...),
):
    try:
        print(
            f"[drive_api][get_non_embedded_files_count] file_ids: {request.file_ids}, batch_size: {request.batch_size}"
        )
        count = await service.get_non_embedded_files_count(
            request.file_ids, request.batch_size
        )
        return {"non_embedded_count": count}
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error getting non-embedded files count: {str(e)}"
        )
