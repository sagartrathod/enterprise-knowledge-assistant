from __future__ import annotations

from fastapi import Depends, UploadFile

from app.api.deps import get_upload_service
from app.core.logger import logger
from app.schemas import MultiUploadResponse
from app.services.upload_service import UploadService


async def upload_pdf(
    files: list[UploadFile],
    upload_service: UploadService = Depends(
        get_upload_service,
    ),
) -> MultiUploadResponse:
    """
    Upload multiple PDF controller.

    Business logic and exception handling are delegated
    to the service layer.
    """

    logger.info("=" * 100)
    logger.info("MULTIPLE PDF UPLOAD CONTROLLER")
    logger.info("=" * 100)

    logger.info(
        "Received upload request | Total Files=%d",
        len(files),
    )

    for file in files:
        logger.info("File: %s", file.filename)

    response = await upload_service.process_multiple_pdf_upload(
        files=files,
    )

    logger.info(
        "Upload completed successfully."
    )

    return MultiUploadResponse(
        **response,
    )