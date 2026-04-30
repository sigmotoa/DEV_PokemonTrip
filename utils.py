import os
from pathlib import Path
import shutil
from fastapi import File, UploadFile, HTTPException

IMG_DIR = Path("files/img")


def save_img_local(file:UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Archivo Invalido")

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    dest = IMG_DIR/file.filename

    with dest.open("wb") as store:
        shutil.copyfileobj(file.file, store)

    return dest





