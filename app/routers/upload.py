from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi import status
import os
import uuid
import aiofiles
from .. import oauth2, models

router = APIRouter(prefix="/upload", tags=["Upload"])

# Fayllar saqlanadigan papka
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Ruxsat etilgan formatlar
ALLOWED_TYPES = {
    "image/jpeg", "image/png",
    "image/gif", "image/webp"
}
MAX_SIZE = 5 * 1024 * 1024   # 5 MB

# ─── RASM YUKLASH ─────────────────────────────
@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Format tekshirish
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faqat rasm formatlar: {ALLOWED_TYPES}"
        )

    # Fayl o'qish
    contents = await file.read()

    # Hajm tekshirish
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fayl hajmi 5 MB dan oshmasin"
        )

    # Noyob fayl nomi
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Faylni saqlash
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    return {
        "filename": filename,
        "url": f"/uploads/{filename}",
        "size": len(contents),
        "content_type": file.content_type,
        "uploaded_by": current_user.username
    }


# ─── KO'P FAYL YUKLASH ────────────────────────
@router.post("/images")
async def upload_multiple(
    files: list[UploadFile] = File(...),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Bir vaqtda max 5 ta fayl"
        )

    results = []
    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            continue

        contents = await file.read()
        extension = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(contents)

        results.append({
            "filename": filename,
            "url": f"/uploads/{filename}",
            "size": len(contents)
        })

    return {"uploaded": results, "count": len(results)}