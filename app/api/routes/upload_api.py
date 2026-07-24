from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_upload_service
from app.controllers.upload_controller import upload_pdf
from app.schemas import MultiUploadResponse
from app.services import UploadService

router = APIRouter(tags=["Upload"])


@router.post(
    "/upload",
    response_model=MultiUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload(
    files: list[UploadFile] = File(...),
    upload_service: UploadService = Depends(get_upload_service),
):
    return await upload_pdf(
        files=files,
        upload_service=upload_service,
    )