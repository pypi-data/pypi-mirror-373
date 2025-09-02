import mimetypes
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import Dict
import os
import tempfile
from pathlib import Path

from botrun_ask_folder.fast_api.jwt_util import verify_token
from botrun_ask_folder.util.file_handler import (
    FailedToExtractContentException,
    HandlePowerpointError,
    UnsupportedFileException,
    handle_file_upload,
)

doc_api_router = APIRouter()


@doc_api_router.post("/doc/content", dependencies=[Depends(verify_token)])
async def get_doc_content_endpoint(
    file: UploadFile = File(...), file_name: str = Form(...)
) -> Dict:
    try:
        # 更安全地處理檔案副檔名
        original_name = Path(file_name)
        file_ext = "".join(original_name.suffixes)  # 處理多重副檔名，如 .tar.gz
        if not file_ext:
            # 如果沒有副檔名，嘗試從 content_type 推測
            mime_type = file.content_type
            if mime_type:
                guess_ext = mimetypes.guess_extension(mime_type)
                file_ext = guess_ext if guess_ext else ""

        # 在臨時目錄中建立檔案，使用原始檔名但確保安全
        with tempfile.NamedTemporaryFile(
            suffix=file_ext.lower(), delete=False
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # 使用 get_doc_content 提取文件內容
            error_msg, text_content = await get_doc_content(temp_path)

            if error_msg:
                raise HTTPException(status_code=400, detail=error_msg)

            return {
                "success": True,
                "file_name": file_name,
                "text_content": text_content,
            }

        finally:
            # 確保清理臨時檔案
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except (
        UnsupportedFileException,
        FailedToExtractContentException,
        HandlePowerpointError,
    ) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )


async def get_doc_content(file_path: str) -> tuple[str, str]:
    """獲取文件內容，並確保正確處理 MIME 類型"""
    file_name = os.path.basename(file_path)

    # 1. 先嘗試使用 mimetypes
    file_mime = mimetypes.guess_type(file_path)[0]

    # 2. 如果 mimetypes 返回 None，使用擴展名映射
    if file_mime is None:
        ext = os.path.splitext(file_path)[1].lower()
        mime_map = {
            ".txt": "text/plain",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".htm": "text/html",
        }
        file_mime = mime_map.get(ext)

    try:
        content = await handle_file_upload(file_name, file_path, file_mime)
        return "", content
    except UnsupportedFileException as e:
        return f"目前不支援這個檔案類型: {file_mime}", ""
    except FailedToExtractContentException as e:
        return f"無法從檔案 {file_name} 取得內容", ""
    except HandlePowerpointError as e:
        return f"無法處理 PowerPoint 文件: {str(e)}", ""
