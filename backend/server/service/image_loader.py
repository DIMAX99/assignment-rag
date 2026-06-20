import httpx
from fastapi import HTTPException

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


async def download_image_from_url(image_url: str):
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(image_url)
            response.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not download image from the provided URL"
        )

    content_type = response.headers.get("content-type", "").split(";")[0]

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type: {content_type}"
        )

    image_bytes = response.content

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB"
        )

    return {
        "image_bytes": image_bytes,
        "content_type": content_type,
        "size": len(image_bytes),
    }