import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile


# app directory
APP_DIR = Path(__file__).resolve().parent.parent

# permanent upload location
UPLOAD_DIR = APP_DIR / "upload"


def save_temporary_file(
    upload_file: UploadFile,
    destination_directory: str = str(UPLOAD_DIR)
) -> str:
    """
    Saves uploaded PDF locally.
    """

    os.makedirs(
        destination_directory,
        exist_ok=True
    )


    original_name = os.path.basename(
        upload_file.filename
    )

    safe_filename = (
        f"{uuid.uuid4()}_{original_name}"
    )


    file_path = os.path.join(
        destination_directory,
        safe_filename
    )


    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            upload_file.file,
            buffer
        )


    return file_path



def remove_file_safely(
    file_path: str
) -> None:
    """
    Removes temporary files safely.
    """

    try:

        if os.path.exists(file_path):

            os.remove(
                file_path
            )

    except Exception as e:

        print(
            f"File cleanup failed: {e}"
        )