import os
import shutil
import uuid
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "src/media"


@router.post("/bytes")
async def upload_bytes(file: Annotated[bytes, File(...)]):
    return {"file_name": "archivo_subido", "size_bytes": len(file)}


@router.post("/file")
async def upload_file(file: UploadFile):
    return {"file_name": file.filename, "content_type": file.content_type}


@router.post("/save")
def save_file(file: UploadFile):
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imágenes PNG o JPEG",
        )

    ext = os.path.splitext(file.filename)[1]  # .png, .jpeg
    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "file_name": file_name,
        "content_type": file.content_type,
        "url": f"/media/{file_name}",
    }
