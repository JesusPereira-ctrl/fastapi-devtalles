from typing import Annotated

from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/upload", tags=["uploads"])


@router.post("/bytes")
async def upload_bytes(file: Annotated[bytes, File(...)]):
    return {"file_name": "archivo_subido", "size_bytes": len(file)}


@router.post("/file")
async def upload_file(file: UploadFile):
    return {"file_name": file.filename, "content_type": file.content_type}
