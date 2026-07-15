# app/api/v1/upload_controller.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.schemas import UploadResponse
from app.services import UploadService
from app.api.deps import get_upload_service

router = APIRouter()

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service)
):
    """
    Accepts a single PDF file, chunks text blocks, indexes spatial geometry,
    and returns processing logs.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported by this service."
        )
        
    try:
        result = await upload_service.process_pdf_upload(file)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing document pipeline: {str(e)}"
        )