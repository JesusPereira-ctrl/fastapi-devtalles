from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from src.services.file_storage import save_uploaded_image

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "src/media"


@router.post("/bytes")
async def upload_bytes(file: Annotated[bytes, File(...)]):
    return {"file_name": "archivo_subido", "size_bytes": len(file)}


@router.post("/file")
async def upload_file(file: UploadFile):
    return {"file_name": file.filename, "content_type": file.content_type}


@router.post("/save")
async def save_file(file: UploadFile):
    saved = save_uploaded_image(file)

    return {
        "file_name": saved["file_name"],
        "content_type": saved["content_type"],
        "url": saved["url"],
    }
